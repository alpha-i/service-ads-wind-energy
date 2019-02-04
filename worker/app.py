from celery import Celery

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, QUEUE_VISIBILITY_TIMEOUT

celery = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


def make_celery():
    celery = Celery(
        backend=CELERY_RESULT_BACKEND,
        broker=CELERY_BROKER_URL
    )
    # default visibility is 1hr, which may cause tasks to be resubmitted
    # if they're sitting behind a long-running taks
    celery.conf['broker_transport_options'] = {
        'visibility_timeout': QUEUE_VISIBILITY_TIMEOUT
    }
    return celery
