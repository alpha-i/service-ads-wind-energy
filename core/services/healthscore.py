from core.models import Healthscore


def get_last_healthscore_for_turbine(turbine_id_list):

    Healthscore.query

    """
    SELECT turbine_id, component_code, value, timestamp from
    healthscore
    where component_code = 'global_model'
    group by turbine_id
    
    order by timestamp desc
    """

