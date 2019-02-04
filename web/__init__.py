from pathlib import Path

from flask import Flask, request, render_template

from core.content import ApiResponse
from core.jsonencoder import CustomJSONEncoder


def create_app(config_filename):
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    app.config.from_object(config_filename)

    from core.database import init_db, db_session
    init_db()

    from web.views.main import home_blueprint
    from web.views.user import user_blueprint
    from web.views.windfarm import windfarm_blueprint
    from web.views.maintenance import maintenance_blueprint
    from web.views.alerts import alerts_blueprint
    from web.views.settings import settings_blueprint
    from web.views.company import company_blueprint
    from web.views.authentication import authentication_blueprint
    from web.views.dashboard import dashboard_blueprint
    from web.views.data_exploration import data_exploration_blueprint
    app.register_blueprint(home_blueprint, url_prefix='/')
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    app.register_blueprint(windfarm_blueprint, url_prefix='/windfarm')
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(authentication_blueprint, url_prefix='/auth')
    app.register_blueprint(company_blueprint, url_prefix='/company')
    app.register_blueprint(maintenance_blueprint, url_prefix='/maintenance')
    app.register_blueprint(alerts_blueprint, url_prefix='/alerts')
    app.register_blueprint(data_exploration_blueprint, url_prefix='/exploration')
    app.register_blueprint(settings_blueprint, url_prefix='/settings')

    @app.before_request
    def before_request():
        # When you import jinja2 macros, they get cached which is annoying for local
        # development, so wipe the cache every request.
        if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
            app.jinja_env.cache = {}

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.errorhandler(404)
    def render_404(e):
        response = ApiResponse(
            content_type=request.accept_mimetypes.best,
            context={'message': e.description},
            template='404.html',
            status_code=404
        )
        return response()

    @app.errorhandler(401)
    def render_401(e):
        response = ApiResponse(
            content_type=request.accept_mimetypes.best,
            context={'message': e.description},
            template='401.html',
            status_code=401
        )
        return response()

    @app.errorhandler(400)
    def render_400(e):
        response = ApiResponse(
            content_type=request.accept_mimetypes.best,
            context={'message': e.description},
            template='400.html',
            status_code=400
        )
        return response()

    @app.errorhandler(500)
    def render_500(e):
        # We don't want to show internal exception messages...
        return render_template('500.html'), 500

    app.json_encoder = CustomJSONEncoder

    # for folder in ['UPLOAD_ROOT_FOLDER', 'TEMPORARY_UPLOAD_FOLDER', 'TRAIN_ROOT_FOLDER', 'WINDFARM_CONFIGURATION_FOLDER']:
    #     path = Path(app.config[folder])
    #     path.mkdir(parents=True, exist_ok=True)

    return app
