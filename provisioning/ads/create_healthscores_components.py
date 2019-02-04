import random
import sys
import csv
import numpy as np

from core.database import db_session
from core.models.health import WindFarmHealthScore, ComponentHealth, TurbineHealth, GroupVariableHealth
from core.services.windfarm import build_windfarm_for_company


def to_component_id(component_name):
    return component_name.lower().replace(' ', '_')



if __name__ == '__main__':
    fake_data_csv = open('./provisioning/ads/fake_data.csv')
    reader = csv.DictReader(fake_data_csv)

    windfarm_object = build_windfarm_for_company(company_id=1)

    wf_health_score = WindFarmHealthScore(
        company_id=1
    )

    for turbine_id, row in enumerate(reader):
        turbine_id += 1
        drive_train = row['Drive Train']
        nacelle_yaw = row['Nacelle / Yaw']
        rotor_hub = row['Rotor Hub']
        power_characteristics = row['Rotor Hub']

        est_residual_time = int(float(row['Est. Residual time']))
        downtime = row['Downtime']
        revenue_loss = int(float(row['Revenue Loss']))
        availability = row['Availability']
        capacity_factor = row['Efficiency']
        mean_time_between_fail = int(float(row['Mean time between failures']))
        tower = row['Tower']
        turbine_performance = row['Turbine Performance']

        turbine_health = TurbineHealth(
            company_id=1,
            turbine_id=turbine_id,
            estimated_residual_time=est_residual_time,
            estimated_cost_of_repair=0.0,
            downtime=downtime,
            revenue_loss=revenue_loss,
            failure_cost=0.0,
            availability=availability,
            efficiency=capacity_factor,
            time_between_failures=mean_time_between_fail,
        )

        components = [
            ComponentHealth(
                company_id=1,
                component_id='drive_train',
                component_name='Drive Train',
                score=drive_train
            ),
            ComponentHealth(
                company_id=1,
                component_id='nacelle_yaw',
                component_name='Nacelle / Yaw',
                score=nacelle_yaw
            ),
            ComponentHealth(
                company_id=1,
                component_id='rotor_hub',
                component_name='Rotor Hub',
                score=rotor_hub
            ),
            ComponentHealth(
                company_id=1,
                component_id='power_characteristic',
                component_name='Power Characteristics',
                score=power_characteristics
            ),
            ComponentHealth(
                company_id=1,
                component_id='tower',
                component_name='Tower',
                score=tower
            ),
            ComponentHealth(
                company_id=1,
                component_id='turbine_performances',
                component_name='Turbine Performance',
                score=turbine_performance
            ),
        ]

        # for each component, attach the variables'

        for component in components:
            group = windfarm_object.get_group(component.component_id)
            variables = group.variables
            num_of_variables = len(variables)

            largest_score = 60 * (1 + (0.1 * np.random.randn()))
            scores = [largest_score]

            remaining = 100 - largest_score

            for index in range(num_of_variables - 2):
                score = remaining / (num_of_variables - 1 - index)
                score *= 1 + (0.1 * np.random.randn())
                remaining -= score
                scores.append(score)
            scores.append(remaining)

            random.shuffle(variables)
            random.shuffle(scores)

            for score, variable in zip(scores, variables):
                group_vh = GroupVariableHealth(
                    group_variable_id=variable.replace(' ', '_').lower(),
                    group_variable_name=variable,
                    score=score
                )
                component.groups.append(group_vh)


        turbine_health.components = components
        wf_health_score.turbines.append(turbine_health)

    db_session.add(wf_health_score)
    db_session.commit()
