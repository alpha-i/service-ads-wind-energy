from worker.app import make_celery

celery = make_celery()

from worker.tasks.predict import predict_task
celery.tasks.register(predict_task)
