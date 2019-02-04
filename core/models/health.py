from statistics import mean

from sqlalchemy import Column, String, ForeignKey, Integer, Float, DateTime, DECIMAL, and_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.models.base import BaseModel


class WindFarmHealthScore(BaseModel):
    __tablename__ = 'windfarmhealth'

    company_id = Column(ForeignKey('company.id'))
    turbines = relationship('TurbineHealth')

    @classmethod
    def get_by_company_id(cls, company_id):
        return cls.query.filter(cls.company_id == company_id).order_by(cls.created_at.desc()).first()

    @property
    def healthscore(self):
        # We assume that the windfarm health score is the mean of the
        # individual turbines'
        return round(
            mean([turbine.healthscore for turbine in self.turbines]), 2
        )

    @property
    def windfarm(self):
        # Return the WindFarm object to easily reference names and descriptions
        from core.services.windfarm import build_windfarm_for_company
        return build_windfarm_for_company(company_id=self.company_id)


class TurbineHealth(BaseModel):
    __tablename__ = 'turbinehealth'

    company_id = Column(ForeignKey('company.id'))
    turbine_id = Column(Integer, nullable=False)
    windfarm_health_id = Column(ForeignKey('windfarmhealth.id'))
    windfarm_health = relationship('WindFarmHealthScore', back_populates='turbines')
    components = relationship('ComponentHealth')

    # KPIs
    availability = Column(Float)
    efficiency = Column(Float)
    time_between_failures = Column(Float)

    # performance metrics
    estimated_residual_time = Column(Integer)  # days?
    estimated_cost_of_repair = Column(DECIMAL)
    downtime = Column(Float)
    revenue_loss = Column(DECIMAL)
    failure_cost = Column(DECIMAL)

    healthscore = Column(DECIMAL, nullable=False, default=0)

    @classmethod
    def get_by_turbine_id(cls, company_id, turbine_id):
        health = cls.query.filter(
            cls.company_id == company_id, cls.turbine_id == turbine_id
        ).order_by(cls.created_at.desc()).first()
        if not health:
            return None
        return health

    @property
    def name(self):
        return self.windfarm_health.windfarm.get_turbine(self.turbine_id).name

    @property
    def description(self):
        return self.windfarm_health.windfarm.get_turbine(self.turbine_id).description

    @classmethod
    def get_latest(cls, company_id, turbine_list):
        stmt = cls.query.session.query(cls.turbine_id, func.max(cls.created_at).label('max_created')).group_by(cls.turbine_id).subquery()

        return cls.query.session.query(cls).join(
            stmt,
            and_(cls.turbine_id == stmt.c.turbine_id, cls.created_at == stmt.c.max_created)
            ).filter(cls.turbine_id.in_(turbine_list)).filter(cls.company_id==company_id).order_by(cls.turbine_id).all()


class ComponentHealth(BaseModel):
    __tablename__ = 'componenthealth'

    # TODO: change the way we identify components
    # probably according to the company configuration yaml
    component_id = Column(String, nullable=False)
    component_name = Column(String, nullable=False)
    company_id = Column(ForeignKey('company.id'))
    parent_turbine_health_id = Column(ForeignKey('turbinehealth.id'))
    turbine_health = relationship('TurbineHealth', back_populates='components')
    score = Column(Float, nullable=True)

    @property
    def labels(self):
        return [group.group_variable_name for group in self.groups]

    @property
    def data(self):
        return [group.score for group in self.groups]
