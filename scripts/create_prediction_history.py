"""
Create mock of prediction results

    For each turbine:
    1 - create a connection on es :
        needed to avoid timeouts
    2 - fetch the full data for the turbine in the window of 1 month ending on 2016/02/29 00:00:00
    3 - cleaning the result dataframe of string columns. filling nan with 0
    4 - normalizing the turbine_dataframe
    5 - for each model, calculating  the average with multiplication to simulate probability
    6 - creating a global_model probability
    7 - writing moked proability to elastic search


sample of the document produced

 {
    "timestamp": "2016-02-29T00:00:00",
    "wind_turbine": 2,
    "drive_train": 42,
    "nacelle_yaw": 68,
    "power_characteristic": 77,
    "rotor_hub": 2,
    "tower": 0,
    "turbine_performances": 46,
    "global_model": 31
  }
"""

from datetime import datetime, timedelta
import time

from elasticsearch import Elasticsearch
from sklearn import preprocessing
import pandas as pd
from alphai_es_datasource.wf import ElasticSearchConnector

from core.services.windfarm import build_windfarm_for_company


delta = timedelta(minutes=10)
start_date = datetime(2016, 1, 31)

models_group = [
    'drive_train',
    'nacelle_yaw',
    'power_characteristic',
    'rotor_hub',
    'tower',
    'turbine_performances',
]

string_columns = [
    'DisconnectorOpen',
    'EventParam-SQL',
    'GasPressure',
    'MVBClose',
    'MVBError',
    'MVBOpen',
    'MVBSF6P2',
    'MVBSF6Pressure',
    'MVBTrip',
    'OilLevel',
    'TurbineReleased',
    'WpsStatus',
    'WTOperationState',
    'ActionsPerformed'
]

# print("Remove this line if you want to execute")
# exit(0)

windfarm = build_windfarm_for_company(2)

index_name = 'wf_model_predictions'
doc_type = 'wf_model_prediction'

turbine_list = range(1, 28)

for turbine_id in turbine_list:

    connector = ElasticSearchConnector(
        host='51.144.39.71:9200',
        index_name='wf_scada_hist',
    )

    es = Elasticsearch('51.144.39.71:9200')

    document_list = []
    print(f"Reading turbine {turbine_id}")
    current_timestamp = datetime(2016, 2, 29)

    variables = set(windfarm.variables()) - set(string_columns)

    historical_turbine_data = connector.get_window(turbines=(turbine_id,),
                                                   start_date=start_date,
                                                   end_date=current_timestamp + delta,
                                                   fields=tuple(variables)
                                                   )
    global_model_data = historical_turbine_data.fillna(0)

    if global_model_data.empty:
        continue

    normalized_turbine_data = (global_model_data - global_model_data.mean()) / global_model_data.std()
    normalized_turbine_data.fillna(0, inplace=True)

    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(normalized_turbine_data.values)
    normalized_turbine_data = pd.DataFrame(x_scaled, index=global_model_data.index, columns=global_model_data.columns)

    while current_timestamp > start_date:
        document_timestamp = int(time.mktime(current_timestamp.timetuple())) * 1000
        document = {
            'timestamp': document_timestamp,
            'wind_turbine': turbine_id
        }

        for model in models_group:

            variables = windfarm.variables(model)
            model_variable_data = normalized_turbine_data.loc[:, variables].copy()

            document[model] = min(model_variable_data.loc[current_timestamp].mean(), 1)

        document['global_model'] = min(normalized_turbine_data.loc[current_timestamp].mean(), 1)

        current_timestamp = current_timestamp - delta

        document_list.append(document)

    print(f"Writing documents for turbine {turbine_id}")
    for document in document_list:
        doc_id = "{}WT{:02d}".format(
            int(document['timestamp']),
            document['wind_turbine']
        )
        try:
            es.delete(index=index_name, doc_type=doc_type, id=doc_id)
        except Exception as e:
            pass

        es.create(
            index=index_name,
            doc_type=doc_type,
            id=doc_id,
            body=document
        )

    time.sleep(5)
