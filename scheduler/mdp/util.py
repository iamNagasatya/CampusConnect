"""PyTorch utilities and custom modules with multiple inputs and valid action enforcement."""

import math
from functools import partial

import numpy as np
import torch
from torch import nn
from torch.nn import functional
from torch.utils.data import DataLoader, Dataset, TensorDataset


def reset_weights(model):
    if hasattr(model, "reset_parameters"):
        model.reset_parameters()


def to_tensor(arr, dtype=torch.float32, device="cpu"):  # TODO: D.R.Y with SB3?
    if isinstance(arr, dict):
        return {key: to_tensor(val, dtype, device) for key, val in arr.items()}
    return torch.tensor(arr, dtype=dtype).to(device)


def flatten_rollouts(a):
    if isinstance(a, dict):
        return {key: flatten_rollouts(val) for key, val in a.items()}
    else:
        return a.reshape(-1, *a.shape[2:])


def valid_logits(x, seq):
    return x - 1e8 * seq


def reward_to_go(rew, gamma=1.0):
    """
    Compute discounted infinite-horizon reward-to-go (i.e. return).

    Parameters
    ----------
    rew : np.ndarray
        Rewards. Shape (n_ep, n_step).
    gamma : float, optional
        Discount factor.

    """
    ret = rew
    for i in reversed(range(rew.shape[-1] - 1)):
        ret[:, i] += gamma * ret[:, i + 1]
    return ret


def obs_to_tuple(obs):
    if isinstance(obs, dict):
        return tuple(obs.values())
    # if obs.dtype.names is not None:
    #     return tuple(obs[key] for key in obs.dtype.names)
    else:
        return (obs,)


def make_dataloaders(obs, act, ret, dl_kwargs=None, frac_val=0.0, dl_kwargs_val=None):
    """Create PyTorch `DataLoader` instances for training and validation."""
    # TODO: RNG control

    n_gen = len(act)

    # Train/validation split
    n_gen_val = math.floor(n_gen * frac_val)
    n_gen_train = n_gen - n_gen_val

    if isinstance(obs, dict):
        arr_train, arr_val = zip(*(np.split(item, [n_gen_train]) for item in obs.values()))
        obs_train = dict(zip(obs.keys(), arr_train))
        obs_val = dict(zip(obs.keys(), arr_val))
    else:
        obs_train, obs_val = np.split(obs, [n_gen_train])
    act_train, act_val = np.split(act, [n_gen_train])
    ret_train, ret_val = np.split(ret, [n_gen_train])

    # Flatten episode data
    obs_train, obs_val, act_train, act_val, ret_train, ret_val = map(
        flatten_rollouts, (obs_train, obs_val, act_train, act_val, ret_train, ret_val)
    )

    # Unpack any `dict`, make tensors
    obs_train = tuple(map(partial(to_tensor, dtype=torch.float32), obs_to_tuple(obs_train)))
    obs_val = tuple(map(partial(to_tensor, dtype=torch.float32), obs_to_tuple(obs_val)))
    act_train, act_val = map(partial(to_tensor, dtype=torch.int64), (act_train, act_val))
    ret_train, ret_val = map(partial(to_tensor, dtype=torch.float32), (ret_train, ret_val))
    # obs_train = tuple(map(partial(torch.tensor, dtype=torch.float32), obs_to_tuple(obs_train)))
    # obs_val = tuple(map(partial(torch.tensor, dtype=torch.float32), obs_to_tuple(obs_val)))
    # act_train, act_val = map(partial(torch.tensor, dtype=torch.int64), (act_train, act_val))
    # ret_train, ret_val = map(partial(torch.tensor, dtype=torch.float32), (ret_train, ret_val))

    # Create data loaders
    ds_train = TensorDataset(*obs_train, act_train, ret_train)
    if dl_kwargs is None:
        dl_kwargs = {}
    dl_train = DataLoader(ds_train, **dl_kwargs)

    if len(ret_val) > 0:
        ds_val = TensorDataset(*obs_val, act_val, ret_val)
        if dl_kwargs_val is None:
            dl_kwargs_val = {}
        dl_val = DataLoader(ds_val, **dl_kwargs_val)
    else:
        dl_val = None

    return dl_train, dl_val


class DictObsDataset(Dataset):
    def __init__(self, obs, act, ret) -> None:
        assert all(act.size(0) == val.size(0) for val in obs.values()), "Size mismatch"
        assert act.size(0) == ret.size(0), "Size mismatch"
        self.obs = obs
        self.act = act
        self.ret = ret

    def __getitem__(self, index):
        return {key: val[index] for key, val in self.obs.items()}, self.act[index], self.ret[index]

    def __len__(self):
        return self.ret.size(0)


def collate_dict_obs(batch):
    obs, act, ret = zip(*batch)
    obs = {key: torch.stack([val[key] for val in obs]) for key in obs[0].keys()}
    act = torch.stack(act)
    ret = torch.stack(ret)
    return obs, act, ret


def make_dataloaders_dict(obs, act, ret, dl_kwargs=None, frac_val=0.0, dl_kwargs_val=None):
    # TODO: RNG control

    n_gen = len(act)

    # Train/validation split
    n_gen_val = math.floor(n_gen * frac_val)
    n_gen_train = n_gen - n_gen_val

    if isinstance(obs, dict):
        arr_train, arr_val = zip(*(np.split(item, [n_gen_train]) for item in obs.values()))
        obs_train = dict(zip(obs.keys(), arr_train))
        obs_val = dict(zip(obs.keys(), arr_val))
    else:
        obs_train, obs_val = np.split(obs, [n_gen_train])
    act_train, act_val = np.split(act, [n_gen_train])
    ret_train, ret_val = np.split(ret, [n_gen_train])

    # Flatten episode data
    obs_train, obs_val, act_train, act_val, ret_train, ret_val = map(
        flatten_rollouts, (obs_train, obs_val, act_train, act_val, ret_train, ret_val)
    )

    # Make tensors
    obs_train, obs_val, ret_train, ret_val = map(
        partial(to_tensor, dtype=torch.float32), (obs_train, obs_val, ret_train, ret_val)
    )
    act_train, act_val = map(partial(to_tensor, dtype=torch.int64), (act_train, act_val))

    # Create data loaders
    ds_train = DictObsDataset(obs_train, act_train, ret_train)
    if dl_kwargs is None:
        dl_kwargs = {}
    dl_train = DataLoader(ds_train, collate_fn=collate_dict_obs, **dl_kwargs)

    ds_val = DictObsDataset(obs_val, act_val, ret_val)
    if dl_kwargs_val is None:
        dl_kwargs_val = {}
    dl_val = DataLoader(ds_val, collate_fn=collate_dict_obs, **dl_kwargs_val)

    return dl_train, dl_val


def build_mlp(layer_sizes, activation=nn.ReLU, last_act=False):
    """
    PyTorch sequential MLP.

    Parameters
    ----------
    layer_sizes : Collection of int
        Hidden layer sizes.
    activation : nn.Module, optional
        Non-linear activation function.
    last_act : bool, optional
        Include final activation function.

    Returns
    -------
    nn.Sequential

    """
    layers = []
    for i, (in_, out_) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
        layers.append(nn.Linear(in_, out_))
        if last_act or i < len(layer_sizes) - 2:
            layers.append(activation())
    return nn.Sequential(*layers)


def build_cnn(layer_sizes, kernel_sizes, pooling_layers=None, activation=nn.ReLU, last_act=False):
    """
    PyTorch sequential CNN.

    Parameters
    ----------
    layer_sizes : Collection of int
        Hidden layer sizes.
    kernel_sizes : int or tuple or Collection of tuple
        Kernel sizes for convolutional layers. If only one value is provided, the same is used for
        all convolutional
        layers.
    pooling_layers : nn.Module or Collection of nn.Module, optional
        Pooling modules. If only one value is provided, the same is used after each convolutional
        layer.
    activation : nn.Module, optional
        Non-linear activation function.
    last_act : bool, optional
        Include final activation function.

    Returns
    -------
    nn.Sequential

    """
    if isinstance(kernel_sizes, int):
        kernel_sizes = (kernel_sizes,)
    if isinstance(kernel_sizes, tuple) and all([isinstance(item, int) for item in kernel_sizes]):
        kernel_sizes = [kernel_sizes for __ in range(len(layer_sizes) - 1)]

    if pooling_layers is None or isinstance(pooling_layers, nn.Module):
        pooling_layers = [pooling_layers for __ in range(len(layer_sizes) - 1)]

    layers = []
    for i, (in_, out_, kernel_size, pooling) in enumerate(
        zip(layer_sizes[:-1], layer_sizes[1:], kernel_sizes, pooling_layers)
    ):
        layers.append(nn.Conv1d(in_, out_, kernel_size=kernel_size))
        if last_act or i < len(layer_sizes) - 2:
            layers.append(activation())
        if pooling is not None:
            layers.append(pooling)
    return nn.Sequential(*layers)


class MultiNet(nn.Module):
    """
    Multiple-input network with valid action enforcement.

    Parameters
    ----------
    net_ch : nn.Module
    net_tasks: nn.Module
    net_joint : nn.Module

    Notes
    -----
    Processes input tensors for channel availability, sequence mask, and tasks. The channel and
    task tensors are separately processed by the respective modules before concatenation and
    further processing in `net_joint`. The sequence mask blocks invalid logits at the output to
    ensure only valid actions are taken.

    """

    def __init__(self, net_ch, net_tasks, net_joint):
        super().__init__()
        self.net_ch = net_ch
        self.net_tasks = net_tasks
        self.net_joint = net_joint

    def forward(self, ch_avail, seq, tasks):
        c, s, t = ch_avail, seq, tasks

        t = t.permute(0, 2, 1)
        t = t * (1 - s).unsqueeze(1)  # masking
        # t = torch.cat((t, (1 - s).unsqueeze(1)), dim=1)

        c = self.net_ch(c)
        t = self.net_tasks(t)

        x = torch.cat((c, t), dim=-1)
        x = self.net_joint(x)

        x = valid_logits(x, s)
        return x

    # TODO: constructors DRY from one another and from SB3 extractors?

    @classmethod
    def mlp(cls, env, hidden_sizes_ch=(), hidden_sizes_tasks=(), hidden_sizes_joint=()):
        layer_sizes_ch = [env.n_ch, *hidden_sizes_ch]
        net_ch = build_mlp(layer_sizes_ch, last_act=True)

        layer_sizes_tasks = [env.n_tasks * env.n_features, *hidden_sizes_tasks]
        # layer_sizes_tasks = [env.n_tasks * (1 + env.n_features), *hidden_sizes_tasks]
        net_tasks = nn.Sequential(nn.Flatten(), *build_mlp(layer_sizes_tasks, last_act=True))

        size_in_joint = layer_sizes_ch[-1] + layer_sizes_tasks[-1]
        layer_sizes_joint = [size_in_joint, *hidden_sizes_joint, env.action_space.n]
        net_joint = build_mlp(layer_sizes_joint)

        return cls(net_ch, net_tasks, net_joint)

    @classmethod
    def cnn(
        cls,
        env,
        hidden_sizes_ch=(),
        hidden_sizes_tasks=(),
        kernel_sizes=2,
        cnn_kwargs=None,
        hidden_sizes_joint=(),
    ):
        layer_sizes_ch = [env.n_ch, *hidden_sizes_ch]
        net_ch = build_mlp(layer_sizes_ch, last_act=True)

        layer_sizes_tasks = [env.n_features, *hidden_sizes_tasks]
        # layer_sizes_tasks = [1 + env.n_features, *hidden_sizes_tasks]
        if cnn_kwargs is None:
            cnn_kwargs = {}
        net_tasks = nn.Sequential(
            *build_cnn(layer_sizes_tasks, kernel_sizes, last_act=True, **cnn_kwargs),
            nn.Flatten(),
        )

        size_in_joint = layer_sizes_ch[-1] + layer_sizes_tasks[-1]
        layer_sizes_joint = [size_in_joint, *hidden_sizes_joint, env.action_space.n]
        net_joint = build_mlp(layer_sizes_joint)

        return cls(net_ch, net_tasks, net_joint)


class VaryCNN(nn.Module):
    def __init__(self, env, kernel_len):  # TODO: add arguments
        super().__init__()

        n_filters = 400

        self.conv_t = nn.Conv1d(env.n_features, n_filters, kernel_size=kernel_len)
        # self.conv_t = nn.Conv1d(1 + env.n_features, n_filters, kernel_size=kernel_len)
        self.conv_ch = nn.Conv1d(1, n_filters, kernel_size=(3,))
        self.conv_x = nn.Conv1d(n_filters, 1, kernel_size=(2,))

    def forward(self, ch_avail, seq, tasks):
        c, s, t = ch_avail, seq, tasks

        t = t.permute(0, 2, 1)
        t = t * (1 - s).unsqueeze(1)  # masking
        t = torch.cat((t, (1 - s).unsqueeze(1)), dim=1)

        t = functional.pad(t, (0, self.conv_t.kernel_size[0] - 1))
        t = self.conv_t(t)

        c = functional.pad(c.unsqueeze(1), (0, self.conv_ch.kernel_size[0] - 1), mode="circular")
        c = self.conv_ch(c)
        c = functional.adaptive_max_pool1d(c, (1,))

        x = c + t
        x = functional.relu(x)

        x = functional.pad(x, (0, self.conv_x.kernel_size[0] - 1))
        x = self.conv_x(x)
        x = x.squeeze(dim=1)
        x = functional.relu(x)

        x = valid_logits(x, s)
        return x
