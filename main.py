from functools import partial

import numpy as np
import pandas as pd
from pytorch_lightning.callbacks import EarlyStopping
from pytorch_lightning.utilities.seed import seed_everything
from stable_baselines3.common.callbacks import StopTrainingOnNoModelImprovement
from torch import nn

from scheduler.algorithms import branch_bound, earliest_release
from scheduler.generators import problems as problem_gens
from scheduler.mdp.environments import Index
from scheduler.mdp.reinforcement import (MultiExtractor,
                                         StableBaselinesScheduler,
                                         ValidActorCriticPolicy)
from scheduler.results import evaluate_algorithms_train

np.set_printoptions(precision=3)
pd.options.display.float_format = "{:,.3f}".format
seed = 12345

if seed is not None:
    seed_everything(seed)


# Define scheduling problem and algorithms
problem_gen = problem_gens.Random.continuous_linear_drop(n_tasks=3, n_ch=1, rng=seed)
# problem_gen = problem_gens.Dataset.load('data/continuous_linear_drop_c1t8', repeat=True)

env = Index(problem_gen, sort_func="t_release", reform=True)



learn_params_sb = {
    "frac_val": 0.3,
    "max_epochs": 5,
    "eval_callback_kwargs": dict(
        callback_after_eval=StopTrainingOnNoModelImprovement(1000, min_evals=0, verbose=1),
        n_eval_episodes=10,
        eval_freq=10,
        verbose=1,
    ),
}
sb_model_kwargs = dict(
    policy=ValidActorCriticPolicy,
    policy_kwargs=dict(
        features_extractor_class=MultiExtractor.mlp,
        features_extractor_kwargs=dict(hidden_sizes_ch=[], hidden_sizes_tasks=[]),
        net_arch=[400],
        activation_fn=nn.ReLU,
        normalize_images=False,
        infer_valid_mask=env.infer_valid_mask,
    ),
)
sb_scheduler = StableBaselinesScheduler.make_model(env, "PPO", sb_model_kwargs, learn_params_sb)


algorithms = np.array(
    [
        ("Earilest Release Time", earliest_release, 10),
        ("RL Agent", sb_scheduler, 10),
    ],
    dtype=[("name", "<U32"), ("obj", object), ("n_iter", int)],
)


# Evaluate results
n_gen_learn = 10  # the number of problems generated for learning, per iteration
n_gen = 5  # the number of problems generated for testing, per iteration
n_mc = 1  # the number of Monte Carlo iterations performed for scheduler assessment

loss_mc, t_run_mc = evaluate_algorithms_train(
    algorithms,
    problem_gen,
    n_gen,
    n_gen_learn,
    n_mc,
    solve=True,
    verbose=1,
    plotting=1,
    img_path="loss.png",
    rng=seed,
)

print(t_run_mc)
print("Loss :", loss_mc)
