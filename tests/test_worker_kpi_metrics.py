import datetime

import pytest

from core.models import TurbineHealth
from core.services.analytics.healthscore import EsConfig
from worker.tasks.health_and_kpi import kpi_performance_task


@pytest.fixture('session')
def task_configuration():
    es_history_config = EsConfig(host="51.144.39.71:9200", index_name="wf_scada_hist", document_type="wf_scada_hist")
    es_probability_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_predictions", document_type="wf_model_prediction")
    es_rul_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_ruls", document_type="wf_model_rul")

    return {
        "company_id": 1,
        "turbine_id": 1,
        "end_date": datetime.datetime(2016, 2, 29),
        "window_delta": 1,
        "es_history_config": es_history_config,
        "es_probability_config":  es_probability_config,
        "es_rul_config":  es_rul_config,
        "components_definitions":  []
    }


def test_health_and_kpi_task(task_configuration):

        turbine_health = kpi_performance_task.run(**task_configuration)

        assert isinstance(turbine_health, TurbineHealth)
        assert turbine_health.id > 0



