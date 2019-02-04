from flask import Blueprint, request

from core.auth import requires_access_token
from core.models.training import TrainingTask
from core.schemas import TrainingTaskSchema
from web.views.api.utils import api_list_response

training_api_blueprint = Blueprint('training_api', __name__)


@training_api_blueprint.route('/')
@requires_access_token
def list_training():
    return api_list_response(
        request,
        TrainingTask,
        TrainingTaskSchema(
            many=True,
            only=((
                'name',
                'task_code',
                'type',
                'domain',
                'training_set_size',
                'created_at',
                'status'
            ))
        )
    )
