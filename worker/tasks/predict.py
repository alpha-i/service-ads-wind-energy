import itertools
from typing import Dict

import numpy as np
from alphai_es_datasource.wf import WFDataSource
from alphai_model_store.basemodel import AbstractModel
from alphai_model_store.chunkycnn_rul import RULPredictionList, RULPrediction
from alphai_model_store.transformers.rul import RULTransformer

from core.utils import import_class
from worker.tasks.base import BaseDBTask


class PredictTask(BaseDBTask):
    """
    This is an encapsulation of the model prediction logic

    It needs a configuration to run, and it should be kept somewhere in the database, and from there
    unwrapped and passed down the road.

    It returns a ModelPredictionList, which contains ModelPrediction objects, which contain abnormality,
    class, timestamp and component.
    """
    name = 'prediction_task'

    def run(self, configuration: dict, *args, **kwargs):
        """
        The configuration gives the model the coordinates to find its components

        {
            'model_class': 'alphai_model_store.chunkycnn.ChunkyCNN',
            'model_params': {...},  # dict to be passed as kwargs to the model init
            'datasource_class': 'alphai_es_datasource.wf.WFDataSource',
            'datasource_params': {...},  # dict to be passed as kwargs to the datasource init,
            'transformer_class': '',
            'transformer_params: '',
        }
        """

        model_class = import_class(configuration['model_class'])
        model_params = configuration['model_params']
        datasource_class = import_class(configuration['datasource_class'])
        datasource_params = configuration['datasource_params']
        transformer_class = import_class(configuration['transformer_class'])
        transformer_params = configuration['transformer_params']
        transformer_params['X_max'] = np.array(transformer_params['X_max'])
        transformer_params['X_min'] = np.array(transformer_params['X_min'])

        transformer = transformer_class(**transformer_params)  # type: RULTransformer
        datasource = datasource_class(**datasource_params)  # type: WFDataSource
        model = model_class(**model_params)  # type: AbstractModel
        raw_data = datasource.get_list_of_chunks()  # type: Dict

        # there should be only one turbine at this point, so squash everything together please
        raw_data_squashed = list(itertools.chain(*[raw_data[turbine] for turbine in raw_data]))

        model_data = transformer.transform(raw_data_squashed)

        raw_prediction = model.predict(model_data)  # type: RULPrediction
        normalised_prediction = raw_prediction.results * (model_data.y_max - model_data.y_min) + model_data.y_min
        prediction_denormalised = RULPrediction(results=normalised_prediction)
        prediction = RULPredictionList(
            component=model_params['component_name'],
            data=raw_data_squashed,
            prediction=prediction_denormalised
        )

        return prediction


predict_task = PredictTask()
