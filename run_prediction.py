import argparse
import logging
import os
import pickle
import pprint
from datetime import timedelta, datetime

import yaml

from core.services.analytics.healthscore import EsConfig
from worker.tasks.health_and_kpi import kpi_performance_task
from worker.tasks.predict import predict_task
from worker.tasks.write_results import prediction_writer_task

logging.basicConfig(level=logging.INFO)

transfomer_data = 'transformer_data.pickle'

logging.getLogger('elasticsearch').addHandler(logging.NullHandler())


def parse_turbines(turbine_string) -> tuple:
    return eval(turbine_string)


def parse_config_yaml(yaml_file) -> dict:
    with open(yaml_file) as f:
        return yaml.load(f)


def parse_datetime(date_string) -> datetime:
    return datetime.strptime(date_string, '%Y-%m-%d')


parser = argparse.ArgumentParser(usage="""
Example: python -m run_prediction --turbines '(1,1)' --method run --data-dir ./model_run --day YYYY-MM-DD --window-delta 240 
""")
parser.add_argument('-t', '--turbines', type=parse_turbines)
parser.add_argument('-m', '--method', help="Sets the task running mode. One from run, apply, delay", default='run')
parser.add_argument('-d', '--data-dir', help="Set the location of the transformer params files")
parser.add_argument('-D', '--day', type=parse_datetime, help="set the last day of the prediction window")
parser.add_argument('-w', '--window-delta', help="Set the size of the window of data in hour for the prediction", default=480)

if __name__ == '__main__':
    args = parser.parse_args()
    logging.info("Running prediction")

    configuration = parse_config_yaml(os.path.join(args.data_dir, 'configuration.yaml'))

    end_date = args.day
    start_date = end_date - timedelta(hours=int(args.window_delta))
    turbines = args.turbines  # tuple: (1,)
    method = args.method

    transformer_data = pickle.load(open(os.path.join(args.data_dir, transfomer_data), 'rb'))

    es_history_config = EsConfig(**configuration['elasticsearch']['history'])
    es_probability_config = EsConfig(**configuration['elasticsearch']['probability'])
    es_rul_config = EsConfig(**configuration['elasticsearch']['rul'])

    for model_name, configuration in configuration['models'].items():
        configuration['datasource_params']['host'] = es_history_config.host
        configuration['datasource_params']['index_name'] = es_history_config.index_name
        configuration['datasource_params']['start_date'] = start_date
        configuration['datasource_params']['end_date'] = end_date

        configuration['transformer_params']['X_min'] = transformer_data['X_min']
        configuration['transformer_params']['X_max'] = transformer_data['X_max']

        configuration['saver_config']['es_history_config'] = es_history_config
        configuration['saver_config']['es_probability_config'] = es_probability_config
        configuration['saver_config']['es_rul_config'] = es_rul_config
        configuration['saver_config']['end_date'] = end_date
        configuration['saver_config']['window_delta'] = int(args.window_delta)

        pprint.pprint(configuration, depth=2)  # don't show the averages

        for turbine in range(turbines[0], turbines[1] + 1):
            configuration['datasource_params']['turbines'] = (turbine,)

            try:
                logging.info(f"Running predict for turbine {turbine}")
                run_predict_task = getattr(predict_task, method)
                prediction = run_predict_task(configuration)
                logging.info(f"Prediction completed. Result:")
                pprint.pprint(prediction)

                logging.info(f"Writing prediction on elasticsearch for turbine {turbine}")
                run_prediction_writer = getattr(prediction_writer_task, method)

                # write probability prediction
                run_prediction_writer(turbine, prediction, es_probability_config)

                # write rul prediction
                run_prediction_writer(turbine, prediction, es_rul_config)
                logging.info(f"Writing prediction on elasticsearch for turbine {turbine}")
                run_prediction_writer = getattr(prediction_writer_task, method)
                run_prediction_writer(turbine, prediction, elasticsearch_host)

                logging.info(f"Compute analytics for {turbine}")
                run_kpi_saver_task = getattr(kpi_performance_task, method)
                configuration['saver_config']['turbine_id'] = turbine
                run_kpi_saver_task(**configuration['saver_config'])
            except Exception as e:
                logging.info(e)
                continue
