import numpy as np
import datetime

from alphai_es_datasource.wf import WFDataSource

from core.services.analytics.kpi import availability, capacity_factor, DEFAULT_NOMINAL_PRODUCTION_KWH, time_between_failures


def test_availability():

    turbine_id = 1

    wf_data = WFDataSource(
        host='51.144.39.71:9200',
        index_name='wf_scada_hist',
        start_date=datetime.datetime(2015, 1, 1),
        end_date=datetime.datetime(2016, 2, 29),
        chunk_size=72,
        stride=72,
        abnormal_window_duration=24,
        turbines=(turbine_id,),
        fields=('ActiveEnergyExport', 'WpsStatus'),
    )

    faulty_intervals = wf_data._get_faulty_intervals()[turbine_id]
    data = wf_data._data
    turbine_plain_data = data[data['wind_turbine'] == turbine_id]
    turbine_lifetime = turbine_plain_data.index[-1] - turbine_plain_data.index[0]

    availability_pct = availability(faulty_intervals, turbine_lifetime)

    np.testing.assert_almost_equal(availability_pct, 62.93706293706294, decimal=5)


def test_capacity_factor():
    turbine_id = 1

    wf_data = WFDataSource(
        host='51.144.39.71:9200',
        index_name='wf_scada_hist',
        start_date=datetime.datetime(2015, 1, 1),
        end_date=datetime.datetime(2016, 2, 29),
        chunk_size=72,
        stride=72,
        abnormal_window_duration=24,
        turbines=(turbine_id,),
        fields=('ActiveEnergyExport', 'WpsStatus', 'ActivePower_Avg-SQL-10minAvg'),
    )

    power_data = wf_data._data.loc[wf_data._data['wind_turbine'] == turbine_id]

    capacity_factor_pct = capacity_factor(power_data, DEFAULT_NOMINAL_PRODUCTION_KWH)

    np.testing.assert_almost_equal(capacity_factor_pct, 46.66952038294197, decimal=5)


def test_mean_between_failures():
    turbine_id = 1

    wf_data = WFDataSource(
        host='51.144.39.71:9200',
        index_name='wf_scada_hist',
        start_date=datetime.datetime(2015, 1, 1),
        end_date=datetime.datetime(2016, 2, 29),
        chunk_size=72,
        stride=72,
        abnormal_window_duration=24,
        turbines=(turbine_id,),
        fields=('ActiveEnergyExport', 'WpsStatus'),
    )

    faulty_intervals = wf_data._get_faulty_intervals()[turbine_id]
    data = wf_data._data.loc[wf_data._data["wind_turbine"] == turbine_id]

    start = data.index[0]
    end = data.index[-1]

    mean_time = time_between_failures(faulty_intervals, start, end)

    assert mean_time.days == 14
