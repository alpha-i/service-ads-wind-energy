from flask import g, request, Blueprint

from core.auth import requires_access_token
from core.content import ApiResponse


dashboard_blueprint = Blueprint('dashboard', __name__)


@dashboard_blueprint.route('/')
@requires_access_token
def index():
    response = ApiResponse(
        content_type=request.accept_mimetypes.best,
        context={},
        template='dashboard.html'
    )

    return response()
