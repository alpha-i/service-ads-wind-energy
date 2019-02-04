from flask import Blueprint, request

from core.auth import requires_access_token
from core.models.detection import DetectionTask
from core.schemas import DetectionTaskSchema
from web.views.api.utils import api_list_response

detection_api_blueprint = Blueprint('detection_api', __name__)


@detection_api_blueprint.route('/')
@requires_access_token
def list_detections():
    return api_list_response(
        request,
        DetectionTask,
        DetectionTaskSchema(many=True, only=(
            'task_code',
            'name',
            'type',
            'created_at',
            'datasource.upload_code',
            'datasource.name',
            'status'
        )),
    )
