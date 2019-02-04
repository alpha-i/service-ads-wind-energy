import datetime
from collections import namedtuple

from alphai_es_datasource.wf import WFDataSource
from alphai_es_datasource.utils import FaultInterval

DEFAULT_NOMINAL_PRODUCTION_KWH = 2300
PRODUCTION_FIELD = "ActivePower_Avg-SQL-10minAvg"

KpiData = namedtuple('KpiData', 'availability capacity_factor time_between_failures')


def availability(faulty_intervals, turbine_lifetime):
    """
    Calculate turbine availability percentage given the faulty intervals and the turbine lifetime
    :param list faulty_intervals: list of faulty interval as calculated by a datasource
    :param datetime.timedelta turbine_lifetime:

    :return float:
    """

    turbine_unavailability = sum([interval.duration for interval in faulty_intervals], datetime.timedelta())

    turbine_availability = turbine_lifetime - turbine_unavailability
    return 100 * turbine_availability.seconds / turbine_lifetime.seconds


def capacity_factor(power_data, nominal_production):
    """
    Calculates capacity factor for turbine using the turbine data and the nominal production in KWH

    :param pd.DataFrame power_data: dataframe containing the ActiveEnergyPowerField
    :param int nominal_production: nominal production of the turbine
    :return:
    """
    power_data = power_data.loc[(power_data["IsFaulty"] == 0) & (power_data[PRODUCTION_FIELD] > 0)][PRODUCTION_FIELD]

    return (power_data.mean() / nominal_production) * 100


def _compute_good_intervals(faulty_intervals, dataframe_start, dataframe_end):

    null_interval_start = [FaultInterval(start=None, end=dataframe_start, duration=datetime.timedelta(0))]
    null_interval_end = [
        FaultInterval(start=dataframe_end, end=None, duration=datetime.timedelta(0))
    ]

    full_interval_list = null_interval_start + sorted(faulty_intervals, key=lambda x: x.start) + null_interval_end
    interval_pairs = list(zip(full_interval_list[::1], full_interval_list[1::1]))
    good_intervals = []
    for left_interval, right_interval in interval_pairs:

        start = left_interval.end
        end = right_interval.start
        if not start or not end:
            duration = None
        else:
            duration = end - start

        good_intervals.append(
            FaultInterval(start=start, end=end, duration=duration)
        )

    return good_intervals


def time_between_failures(faulty_intervals, start, end):

    good_intervals = _compute_good_intervals(faulty_intervals, start, end)

    return sum([interval.duration for interval in good_intervals], datetime.timedelta()) / len(good_intervals)


class KpiCalculator:

    WINDOW_DELTA = datetime.timedelta(days=800)

    def __init__(self, es_config, turbine_id, end_date):

        start_date = end_date - self.WINDOW_DELTA
        datasource = WFDataSource(
            host=es_config.host,
            index_name=es_config.index_name,
            start_date=start_date,
            end_date=end_date,
            chunk_size=72,
            stride=72,
            abnormal_window_duration=240,# not relevant for this class
            turbines=(turbine_id,),
            fields=('ActiveEnergyExport', 'WpsStatus', 'ActivePower_Avg-SQL-10minAvg'),
        )

        self._turbine_faulty_intervals = datasource._get_faulty_intervals()[turbine_id]
        self._turbine_data = datasource._data[datasource._data['wind_turbine'] == turbine_id].copy()

        self._data_start = self._turbine_data.index[0]
        self._data_end = self._turbine_data.index[-1]

    def get_kpi(self):

        return KpiData(
            availability=self._availability(),
            capacity_factor=self._capacity_factor(),
            time_between_failures=self._time_between_failures()
        )

    def _availability(self):
        turbine_lifetime =  self._data_end - self._data_start

        return availability(self._turbine_faulty_intervals, turbine_lifetime)

    def _capacity_factor(self):

        return capacity_factor(self._turbine_data, DEFAULT_NOMINAL_PRODUCTION_KWH)

    def _time_between_failures(self):

        return time_between_failures(
            self._turbine_faulty_intervals,
            self._data_start,
            self._data_end
        )
