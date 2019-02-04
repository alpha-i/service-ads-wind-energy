from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from core.services.analytics.healthscore import (
    get_probabilities, last_probability_healthscore, get_rul, last_rul_healthscore,
    residual_time, EsConfig)


def test_get_probabilities():
    es_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_predictions", document_type="wf_model_prediction")

    turbine_id = 1

    end_date = datetime(2016, 2, 29)
    window_delta = timedelta(days=10)
    probabilities = get_probabilities(turbine_id, end_date, window_delta, es_config)

    assert isinstance(probabilities, pd.DataFrame)
    indexes = probabilities.index

    assert indexes[0] == pd.Timestamp(end_date - window_delta)
    assert indexes[-1] == end_date


def test_last_probability_healthscore():
    es_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_predictions",
                         document_type="wf_model_prediction")

    turbine_id = 1

    end_date = datetime(2016, 2, 29)
    window_delta = timedelta(days=10)
    probabilities = get_probabilities(turbine_id, end_date, window_delta, es_config)

    global_model_score = last_probability_healthscore(probabilities['global_model'])

    np.testing.assert_almost_equal(global_model_score, 88.11894166872555, decimal=5, verbose=True)


def test_get_rul():
    es_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_ruls", document_type="wf_model_rul")
    turbine_id = 1

    end_date = datetime(2016, 2, 29)
    window_delta = timedelta(days=10)
    ruls = get_rul(turbine_id, end_date, window_delta, es_config)

    assert isinstance(ruls, pd.DataFrame)
    indexes = ruls.index

    assert indexes[0] == pd.Timestamp(end_date - window_delta)
    assert indexes[-1] == end_date


def test_last_rul_healthscore():
    es_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_ruls", document_type="wf_model_rul")
    turbine_id = 1

    end_date = datetime(2016, 2, 29)
    window_delta = timedelta(hours=1)
    ruls = get_rul(turbine_id, end_date, window_delta, es_config)

    global_model_rul_healthscore = last_rul_healthscore(ruls['global_model'])

    assert 0 <= global_model_rul_healthscore <= 100


def test_residual_time():
    es_config = EsConfig(host="51.144.39.71:9200", index_name="wf_model_ruls", document_type="wf_model_rul")
    turbine_id = 1

    end_date = datetime(2016, 2, 29)
    window_delta = timedelta(days=10)
    ruls = get_rul(turbine_id, end_date, window_delta, es_config)
    res_time = residual_time(ruls['global_model'])

    np.testing.assert_almost_equal(res_time, 10.662488246015524, decimal=5, verbose=True)
