# dash-celery-integration

Enhancement proposal for dash to integrate with celery tasks/signatures/canvas workflows seamlessly, logged as [Feature Request](https://github.com/plotly/dash/issues/2124).

This is not (yet) a Pull-Request, as the CeleryManager is being refactored at the moment and I'm keen on feedback from Celery and Dash experts first.

The module `celery_manager_tasks` provides a drop in replacement for the `CeleryLongCallbackManager`.
It allows to return tasks or signatures, which (eventually when executed by the celery workers) will provide the result back to dash.

The example program will start 100 `embarassingly_parallel` tasks, returning the task PID after a short sleep. The `collect` task will provide a summary statistics about the runner utilsiation to dash.

The project should (hopefully) work out of the box, starting 3 programms

* a redis server
* a celery worker with `celery -A celery_integration.celery_app worker`, and
* the dash application with `python -m celery_integration`

The application should be read with a "start" button at http://127.0.0.1:8050.

I have developed this example on a Ubuntu Linux 22 box using conda/mamba with
* `python` 3.10.5
* `dash` 2.5.1
* `celery` 5.2.7
* `redis` 7

`mamba env create` should do the trick and provide a conda environment named `celery-integration`.
