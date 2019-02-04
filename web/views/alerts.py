from flask import g, Blueprint, render_template, request, redirect, url_for

from core.auth import requires_access_token
from core.database import db_session
from core.models import Alert

alerts_blueprint = Blueprint('alerts', __name__)


@alerts_blueprint.route('/', methods=['GET'])
@requires_access_token
def index():
    company_id = g.user.company_id
    alerts = Alert.get_for_company_id(company_id)
    return render_template('alerts/list.html', alerts=alerts)

@alerts_blueprint.route('/<string:alert_id>', methods=['POST'])
@requires_access_token
def edit(alert_id):
    note = request.form.get('note')
    alert = Alert.query.filter(Alert.id==alert_id).one_or_none()
    alert.note = note

    db_session.add(alert)
    db_session.commit()

    return redirect(url_for('alerts.index'))
