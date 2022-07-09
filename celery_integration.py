from collections import defaultdict
import os
import time
import random
import uuid

from celery import Celery, chord

import dash
from dash import html


from celery_manager_tasks import CeleryManagerTasks


celery_app = Celery(
    "celery-integration",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)


@celery_app.task
def embarassing_parallel(_):
    time.sleep(random.uniform(0.001, 0.1))
    return os.getpid()


@celery_app.task
def collect(all_results):
    pid_stats = defaultdict(int)
    for pid in all_results:
        pid_stats[pid] += 1

    return '\n'.join(f"worker {pid}: {count} calls"
                     for pid, count in pid_stats.items())


long_callback_manager = CeleryManagerTasks(
    celery_app,
)

dash_app = dash.Dash(
    __name__,
    long_callback_manager=long_callback_manager,
)

dash_app.layout = html.Div(
    [html.Button(id="start-callback", children="start"),
     html.Div(id="callback-output", style={"white-space": "pre-wrap"})]
)


@dash_app.long_callback(
    dash.Output("callback-output", "children"),
    dash.Input("start-callback", "n_clicks"),
)
def celery_callback(_):
    return chord(
        [embarassing_parallel.s(uuid.uuid4().hex) for _ in range(100)],
        collect.s()
    )


if __name__ == "__main__":
    dash_app.run(debug=True)