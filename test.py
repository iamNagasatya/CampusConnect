from matplotlib import pyplot as plt

from scheduler import algorithms
from scheduler.tasks import LinearDrop
from scheduler.util import (check_schedule, evaluate_schedule, plot_schedule,
                            plot_task_losses, summarize_tasks)

seed = 99

# Define scheduling problem


tasks = [
    LinearDrop(duration=2, t_release=1, t_drop=3, l_drop=200, slope=1.5, name="Important Task"),
    LinearDrop(duration=1, t_release=0, t_drop=3, l_drop=100, slope=1, name="Normal Task"),
]
ch_avail = [0.0]

print(summarize_tasks(tasks))
plot_task_losses(tasks)
plt.savefig("Tasks.png")


# Define and assess algorithms
algorithms = dict(
    Optimal=algorithms.branch_bound_priority,
)

for name, algorithm in algorithms.items():
    sch = algorithm(tasks, ch_avail)

    order = sch["t"].astype(int).tolist()
    print(order)
    
    check_schedule(tasks, sch)
    loss = evaluate_schedule(tasks, sch)
    print(loss)
    plot_schedule(tasks, sch, loss=loss, name=name)
    plt.savefig(f"{name}.png")
