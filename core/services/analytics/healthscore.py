from collections import namedtuple

import pandas as pd
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
from alphai_es_datasource.utils import hits_to_dataframe

SCALING_FACTOR = 78 #!!!DEPENDS ON Y_MAX ON THE TRANSFORMER

HealthScore = namedtuple('HealthScore', 'healthscore residual_time cost_of_repair downtime revenue_loss failure_cost')

EsConfig = namedtuple('EsConfig', 'host index_name document_type')


def get_probabilities(turbine_id, end_date, window_delta, es_config):

    """
    Fetch the data from the prediction result and returns a dataframe
    :param int turbine_id:
    :param datetime.datetime end_date:
    :param datetime.timedelta window_delta:
    :param EsConfig es_config:
    :return:
    """

    elastic = Elasticsearch(es_config.host)

    s = Search(using=elastic, index=es_config.index_name)
    s = s.filter("terms", wind_turbine=(turbine_id,))

    start_date = end_date - window_delta
    s = s.filter("range", timestamp={
            "gte": start_date,
            "lte": end_date})
    s = s.sort('timestamp')

    return hits_to_dataframe(list(s.scan()))


def get_rul(turbine_id, end_date, window_delta, es_config):
    """
    Fetch the data from the RUL result and returns a dataframe
    :param int turbine_id:
    :param datetime.datetime end_date:
    :param datetime.timedelta window_delta:
    :param EsConfig es_config:
    :return:
    """

    elastic = Elasticsearch(es_config.host)

    s = Search(using=elastic, index=es_config.index_name)
    s = s.filter("terms", wind_turbine=(turbine_id,))

    start_date = end_date - window_delta
    s = s.filter("range", timestamp={
        "gte": start_date,
        "lte": end_date})
    s = s.sort('timestamp')

    return hits_to_dataframe(list(s.scan()))


def last_probability_healthscore(anomaly_probabilities):
    """
    Calculate last_probability_healthscore as a Exponentially-weighted moving average of the anomaly_probabilities list
    :param list anomaly_probabilities:
    :return float: the anomaly score between 0 an 100
    """

    result = pd.ewma(anomaly_probabilities, span=10)

    return 100 - (result.iloc[-1] * 100)


def last_rul_healthscore(rul_result):
    """
    Return the value of the last RUL converted in a range between 0 and 100

    :param rul_result:
    :return:
    """
    value = rul_result.iloc[-1]

    return min(value / SCALING_FACTOR * 100, 100)


def residual_time(rul_result):
    """
    Return residual time in days calculated with the ewma of the latest  rul
    :param rul_result:
    :return:
    """
    result = rul_result.ewm(span=10).mean()

    return min(result.iloc[-1] / SCALING_FACTOR * 100, 100)


class PerformanceMetrics:

    def __init__(self, es_probability_config, es_rul_config, end_date, window_delta, turbine_id):

        self.window_delta = window_delta
        self.end_date = end_date

        self._probabilities = get_probabilities(
            turbine_id,
            self.end_date,
            self.window_delta,
            es_probability_config
        )

        self._ruls = get_rul(
            turbine_id,
            self.end_date,
            self.window_delta,
            es_rul_config
        )

    def get_performance_metrics(self, component='global_model'):
        return HealthScore(
            healthscore=self._get_rul_healthscore(component),
            residual_time=self._get_residual_time(component),
            cost_of_repair=self._get_cost_of_repair(),
            downtime=self._get_downtime(),
            revenue_loss=self._get_revenue_loss(),
            failure_cost=self._get_failure_cost(),
        )

    def _get_rul_healthscore(self, component):
        return last_rul_healthscore(self._ruls[component])

    def _get_residual_time(self, component):
        return residual_time(self._ruls[component])

    def _get_cost_of_repair(self):
        return 0

    def _get_downtime(self):
        return 0

    def _get_revenue_loss(self):
        return 0

    def _get_failure_cost(self):
        return 0

