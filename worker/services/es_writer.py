import logging
import time
from typing import List, Dict

from alphai_es_datasource.utils import ModelPredictionList, ModelPrediction
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from core.services.analytics.healthscore import EsConfig


def convert_prediction_result_to_prediction_document(turbine, prediction_result: ModelPredictionList,
                                                     es_config: EsConfig) -> List[Dict]:
    logging.info(f"Converting prediction for turbine {turbine}")
    for prediction in prediction_result:  # type: ModelPrediction
        component, timestamp, result = prediction
        unix_timestamp = int(time.mktime(timestamp.to_pydatetime().timetuple()) * 1000)
        yield {
            '_index': es_config.index_name,
            '_type': es_config.document_type,
            '_id': "{}WT{:02d}".format(
                unix_timestamp,
                turbine
            ),
            'wind_turbine': int(turbine),
            component: float(result),
            'timestamp': unix_timestamp
        }


def write_prediction_result_to_elasticsearch(host: str, prediction_results: List[Dict]) -> None:
    es_client = Elasticsearch(hosts=host)
    logging.info(f"Writing prediction {prediction_results} into backend")
    bulk(es_client, prediction_results)
    logging.info("ES Writing done!")
