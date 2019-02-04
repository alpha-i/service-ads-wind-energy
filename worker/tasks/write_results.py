from alphai_es_datasource.utils import ModelPredictionList

from core.services.analytics.healthscore import EsConfig
from worker.services.es_writer import (
    write_prediction_result_to_elasticsearch, convert_prediction_result_to_prediction_document
)
from worker.tasks.base import BaseDBTask


class PredictionWriterTask(BaseDBTask):
    def run(self, turbine: int, prediction_result: ModelPredictionList, es_config: EsConfig, *args, **kwargs):
        es_document = convert_prediction_result_to_prediction_document(turbine, prediction_result, es_config)
        write_prediction_result_to_elasticsearch(host=es_config.host, prediction_results=es_document)


prediction_writer_task = PredictionWriterTask()
