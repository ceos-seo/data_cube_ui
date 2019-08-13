import celery
from celery.task import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from datetime import datetime, timedelta
import shutil
from django.apps import apps

from .models import Application


class DCAlgorithmBase(celery.Task):
    """Serves as a base class for all DC algorithm celery tasks"""
    app_name = None

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Onfailure call for celery tasks

        all tasks should have a kwarg 'task_id' that can be used to 'get' the model
        from the app.

        """
        task_id = kwargs.get('task_id')
        camel_case = "".join(x.title() for x in self._get_app_name().split('_'))
        task_model = apps.get_model(".".join([self._get_app_name(), camel_case + "Task"]))
        task_model_name = task_model.__name__
        history_model = apps.get_model(".".join([self._get_app_name(), "UserHistory"]))
        try:
            task = task_model.objects.get(pk=task_id)
            if task.complete:
                return
            task.complete = True
            task.update_status("ERROR", "There was an unhandled exception during the processing of your task.")
            task_clean_up.s(task_id=task_id, task_model=task_model_name).apply_async()
            history_model.objects.filter(task_id=task.pk).delete()
        except task_model.DoesNotExist:
            pass

    def _get_app_name(self):
        """Get the app name of the task - raise an error if None"""
        if self.app_name is None:
            raise NotImplementedError(
                "You must specify an app_name in classes that inherit DCAlgorithmBase. See the DCAlgorithmBase docstring for more details."
            )
        return self.app_name

def check_cancel_task(self, task):
    """
    Check if a task was cancelled or has thrown an error. If so, end this task and don't
    call any callbacks, which are usually future signatures in a chain.
    We refresh the model view since if the model status was set to "CANCELLED"
    by Django (apps.dc_algorithm.views.CancelRequest.get()), its view in
    Celery workers may not reflect the relational backing.

    Returns True if the task is cancelled and the calling code should `return`.

    Parameters
    ---------
    self: celery.app.task
        A Celery task instance to cancel processing for.
    task: app-specific task ORM object
        A view of an app's task entry in the Django database.
        `apps.custom_mosaic_tool.models.CustomMosaicToolTask` is one example.
    """
    if task.status in ['CANCELLED', 'ERROR']:
        self.request.chain = None
        return True
    else: # The model view may be outdated, so refresh and check again.
        task.refresh_from_db()
        if task.status in ['CANCELLED', 'ERROR']:
            self.request.chain = None
            return True
        return False

@periodic_task(
    name="dc_algorithm.clear_cache",
    #run_every=(30.0),
    run_every=(crontab(hour=0, minute=0)),
    ignore_result=True)
def clear_cache():
    _apps = Application.objects.all()
    time_threshold = datetime.now() - timedelta(days=2)
    for app in _apps:
        camel_case = "".join(x.title() for x in app.pk.split('_'))
        task_model = apps.get_model(".".join([app.pk, camel_case + "Task"]))
        history_model = apps.get_model(".".join([app.pk, "UserHistory"]))
        tasks = task_model.objects.filter(execution_start__lt=time_threshold)
        for task in tasks:
            history_model.objects.filter(task_id=task.pk).delete()
            shutil.rmtree(task.get_result_path())
            task.delete()
    print("Cache Cleared.")


@task(name="dc_algorithm.task_clean_up")
def task_clean_up(*args, **kwargs):
    """
    Cleans up after tasks. By default, this involves removing a temporary directory,
    but more can be done on a per-app basis based on the `task_model` kwarg.
    Note that some parameters are kwarg-only due to Celery mechanics rather than convenience.

    Parameters
    ----------
    task_id: UUID or str
        The ID of the Django task.
    task_model: str (kwarg-only)
        The name of the `django.db.models.Model` representing the query task
        for Django (e.g. `apps.custom_mosaic_tool.models.CustomMosaicToolTask`).
    """
    # Note that these imports will not work for Celery workers when outside this function.
    from apps.cloud_coverage.models import CloudCoverageTask
    from apps.coastal_change.models import CoastalChangeTask
    from apps.custom_mosaic_tool.models import CustomMosaicToolTask
    from apps.fractional_cover.models import FractionalCoverTask
    from apps.ndvi_anomaly.models import NdviAnomalyTask
    from apps.slip.models import SlipTask
    from apps.spectral_anomaly.models import SpectralAnomalyTask
    from apps.spectral_indices.models import SpectralIndicesTask
    from apps.tsm.models import TsmTask
    from apps.urbanization.models import UrbanizationTask
    from apps.water_detection.models import WaterDetectionTask

    task_id = str(kwargs.get('task_id', None))
    assert task_id is not None, "The `task_id` argument must be specified as a string " \
                                "keyword argument."
    task_model = kwargs['task_model']
    task = eval("{}.objects.get(pk='{}')".format(task_model, task_id))
    shutil.rmtree(task.get_temp_path())
    return True