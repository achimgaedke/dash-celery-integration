import inspect
import json
import hashlib

from celery.app.task import Task
from celery.canvas import Signature
from dash.long_callback import CeleryLongCallbackManager
from _plotly_utils.utils import PlotlyJSONEncoder


class CeleryManagerTasks(CeleryLongCallbackManager):
    """
    A celery callback manager, which handles celery tasks and signatures.
    """

    def make_job_fn(self, fn, progress, args_deps):
        return _make_job_fn_async(fn, self.handle, progress, args_deps)


def _make_job_fn_async(fn, celery_app, progress, args_deps):
    cache = celery_app.backend

    # Hash function source and module to create a unique (but stable) celery task name
    fn_source = inspect.getsource(fn)
    fn_str = fn_source
    fn_hash = hashlib.sha1(fn_str.encode("utf-8")).hexdigest()

    @celery_app.task(name=f"long_callback_output_{fn_hash}")
    def job_result_fn(user_callback_output, result_key):
        cache.set(result_key, json.dumps(user_callback_output, cls=PlotlyJSONEncoder))

    @celery_app.task(name=f"long_callback_{fn_hash}")
    def job_fn(result_key, progress_key, user_callback_args, fn=fn):
        def _set_progress(progress_value):
            cache.set(progress_key, json.dumps(progress_value, cls=PlotlyJSONEncoder))

        maybe_progress = [_set_progress] if progress else []
        if isinstance(args_deps, dict):
            user_callback_output = fn(*maybe_progress, **user_callback_args)
        elif isinstance(args_deps, (list, tuple)):
            user_callback_output = fn(*maybe_progress, *user_callback_args)
        else:
            user_callback_output = fn(*maybe_progress, user_callback_args)

        # Added cases for celery Task and Signature
        # set the result value with a task added (linked/chained)
        if isinstance(user_callback_output, Task):
            user_callback_output.apply_async(link=job_result_fn.s(result_key))
        elif isinstance(user_callback_output, Signature):
            (user_callback_output | job_result_fn.s(result_key))()
        # Otherwise do everything within this callback
        else:
            cache.set(result_key, json.dumps(user_callback_output, cls=PlotlyJSONEncoder))

    return job_fn