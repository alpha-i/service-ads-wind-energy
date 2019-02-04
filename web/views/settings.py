from flask import Blueprint, render_template

from core.auth import requires_access_token

settings_blueprint = Blueprint('settings', __name__)


@settings_blueprint.route('/', methods=['GET'])
@requires_access_token
def index():
    return render_template('settings/index.html')
