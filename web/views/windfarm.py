import numpy as np
from flask import g, Blueprint, render_template, redirect, url_for

from core.auth import requires_access_token
from core.models import WindFarmHealthScore, TurbineHealth
from core.services.windfarm import create_turbine_list_view
from core.utils import handle_error

windfarm_blueprint = Blueprint('windfarm', __name__)


@windfarm_blueprint.route('/')
@requires_access_token
def index():
    company = g.user.company
    windfarm = company.windfarm_configuration
    id_list = windfarm.turbines.keys()

    latest_turbine_health_list = TurbineHealth.get_latest(company.id, id_list)
    windfarm_health = round(np.mean([turbine.healthscore for turbine in latest_turbine_health_list]), 2)

    scores = [float(turbine.healthscore) for turbine in latest_turbine_health_list]
    distribution, _ = np.histogram(scores, bins=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100))

    turbine_dataset = create_turbine_list_view(latest_turbine_health_list)

    context = {
        "windfarm": windfarm,
        "windfarm_healthscore": windfarm_health,
        "scores": list(reversed(distribution)),
        "turbine_dataset": turbine_dataset
    }

    return render_template("windfarm/index.html", **context)


@windfarm_blueprint.route('/turbine/<int:turbine_id>')
@requires_access_token
def turbine(turbine_id):
    company = g.user.company
    latest_turbine_health_status = TurbineHealth.get_by_turbine_id(
        company_id=company.id, turbine_id=turbine_id
    )

    print(latest_turbine_health_status)

    if not latest_turbine_health_status:
        handle_error(404, f'Turbine with id {turbine_id} not found')
        return redirect(url_for('windfarm.index'))

    context = {
        'turbine': latest_turbine_health_status,
        'windfarm': company.windfarm_configuration,
        'turbine_id': turbine_id}
    return render_template("windfarm/turbine.html", **context)


@windfarm_blueprint.route('/report/<int:turbine_id>')
@requires_access_token
def technical_report(turbine_id):
    company = g.user.company

    turbine = company.windfarm_configuration.get_turbine(turbine_id)


    return render_template('windfarm/technical_report.html', turbine=turbine)
