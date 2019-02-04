import os
import random
from collections import namedtuple

import yaml
from flask import url_for

from config import WINDFARM_CONFIGURATION_FOLDER
from core.models import TurbineHealth

Turbine = namedtuple('Turbine', 'id name description')
VariableGroup = namedtuple('VariableGroup', 'name variables')


def build_windfarm_for_company(company_id, configuration_folder=WINDFARM_CONFIGURATION_FOLDER):
    windfarm_configuration_path = os.path.join(configuration_folder, f'company_{company_id}.yml')
    configuration = yaml.load(open(windfarm_configuration_path))
    return WindFarm(configuration['windfarm_configuration'])


def create_turbine_list_view(turbine_health_list):
    turbine_list = [
        [
            f"<a href='{url_for('windfarm.turbine', turbine_id=turbine.turbine_id)}'>{turbine.name}</a>",
            turbine.description,
            "Siemens 2.3-93",  # TODO: needs to be changed to something configurable
            "6",
            f"{turbine.healthscore}",
            ]
        for turbine in turbine_health_list
    ]
    return {
        "data": turbine_list,
        "columns": ["Turbine name", "Description", "Type", "Age", "Health score"]
    }


class WindFarm:

    def __init__(self, configuration):

        self.name = configuration['name']
        self._turbines = {turbine_id: Turbine(turbine_id, turbine_data['name'], turbine_data['description'])
                          for turbine_id, turbine_data in configuration['turbines'].items()}

        self._groups = {group_name: VariableGroup(group_name, group['variables'])
                        for group_name, group in configuration['variables'].items()}

    @property
    def turbines(self):
        return self._turbines

    @property
    def groups(self):
        return list(self._groups.values())

    def get_group(self, group_code):
        return self._groups.get(group_code)

    def get_turbine(self, turbine_id):
        return self._turbines.get(turbine_id)

    def variables(self, group_name=None):
        if group_name:
            group = self._groups.get(group_name)
            return group.variables
        else:
            all_vars = list(map(lambda x: x.variables, self._groups.values()))
            return [item for sublist_of_vars in all_vars for item in sublist_of_vars]
