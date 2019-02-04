from flask import Blueprint, request

from core.auth import requires_access_token
from core.schemas import DataSourceSchema
from core.models.datasource import DataSource
from web.views.api.utils import api_list_response

datasource_api_blueprint = Blueprint('datasource_api', __name__)


@datasource_api_blueprint.route('/')
@requires_access_token
def list_detections():
    return api_list_response(
        request,
        DataSource,
        DataSourceSchema(many=True, only=(
            'upload_code',
            'name',
            'label',
            'datasource_configuration.name',
            'created_at',
        )),
    )
