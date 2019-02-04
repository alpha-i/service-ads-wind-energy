from flask import g, Blueprint, render_template, redirect, url_for, request

from core.auth import requires_access_token
from core.models.maintenance import MaintenanceEvent
from core.utils import handle_error

from core.database import db_session

maintenance_blueprint = Blueprint('maintenance', __name__)

@maintenance_blueprint.route('/', methods=['GET'])
@requires_access_token
def index():
    company = g.user.company

    maintenance_events = MaintenanceEvent.get_for_company_id(company.id)
    available_turbines = company.windfarm_configuration.turbines

    return render_template('maintenance/list.html',
                           maintenance_events=maintenance_events,
                           turbines=available_turbines)


@maintenance_blueprint.route('/', methods=['POST'])
@requires_access_token
def new():
    company_id = g.user.company_id

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    turbine = request.form.get('turbine')
    component = request.form.get('component')
    reason = request.form.get('reason')
    note = request.form.get('note')

    if not all([start_date, end_date, turbine, component]):
        return handle_error(400, 'Invalid form have been filled')

    new_maintenance = MaintenanceEvent(
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        turbine=turbine,
        component=component,
        reason=reason,
        note=note
    )

    db_session.add(new_maintenance)
    db_session.commit()

    return redirect(url_for('maintenance.index'))

@maintenance_blueprint.route('/delete/<string:maintenance_id>')
@requires_access_token
def delete(maintenance_id):

    maintenance_event = MaintenanceEvent.get_by_id(maintenance_id)
    if maintenance_event:
        db_session.delete(maintenance_event)
        db_session.commit()

    return redirect(url_for('maintenance.index'))
