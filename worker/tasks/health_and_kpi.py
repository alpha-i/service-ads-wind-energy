import datetime

from core.database import db_session
from core.models import WindFarmHealthScore, TurbineHealth, ComponentHealth
from core.services.analytics.healthscore import PerformanceMetrics
from core.services.analytics.kpi import KpiCalculator
from worker.tasks.base import BaseDBTask


class KpiPerformanceTask(BaseDBTask):

    def run(self, company_id, turbine_id, end_date, window_delta, es_history_config, es_probability_config,
            es_rul_config, components_definitions, **kwargs):
        kpi_calculator = KpiCalculator(
            es_history_config,
            turbine_id,
            end_date)

        kpi = kpi_calculator.get_kpi()

        window_delta = datetime.timedelta(hours=window_delta)
        performance_metrics = PerformanceMetrics(
            es_probability_config,
            es_rul_config, end_date, window_delta, turbine_id
        )

        metrics = performance_metrics.get_performance_metrics('global_model')

        windfarm_health_score = WindFarmHealthScore(company_id=company_id)

        turbine_health = TurbineHealth(
            company_id=company_id,
            turbine_id=turbine_id,
            windfarm_health=windfarm_health_score,
            healthscore=metrics.healthscore,
            availability=kpi.availability,
            efficiency=kpi.capacity_factor,
            time_between_failures=kpi.time_between_failures.seconds / 60,
            estimated_residual_time=metrics.residual_time,
            estimated_cost_of_repair=metrics.cost_of_repair,
            downtime=metrics.downtime,
            revenue_loss=metrics.revenue_loss,
            failure_cost=metrics.failure_cost
        )

        list_of_components = []
        for component in components_definitions:
            component_metrics = performance_metrics.get_performance_metrics(component.id)
            list_of_components.append(
                ComponentHealth(
                    company_id=company_id,
                    component_id=component.id,
                    component_name=component.name,
                    score=component_metrics.healthscore
                ))

        db_session.add(turbine_health)
        db_session.commit()

        return turbine_health

kpi_performance_task = KpiPerformanceTask()
