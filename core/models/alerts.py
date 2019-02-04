from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer

from core.models.base import BaseModel


class Alert(BaseModel):
    __tablename__ = 'alerts'

    company_id = Column(ForeignKey('company.id'))
    time = Column(DateTime)
    turbine_id = Column(Integer)
    description = Column(String)
    note = Column(Text)

    @classmethod
    def get_for_company_id(cls, company_id):
        return cls.query.filter(cls.company_id==company_id).order_by(cls.time.desc()).all()

    @property
    def turbine(self):
        from core.services.windfarm import build_windfarm_for_company
        windfarm = build_windfarm_for_company(company_id=self.company_id)
        return windfarm.get_turbine(self.turbine_id)
