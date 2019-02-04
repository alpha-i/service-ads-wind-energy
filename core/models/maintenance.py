from sqlalchemy import Column, String, ForeignKey, DateTime, Text

from core.models.base import BaseModel


class MaintenanceEvent(BaseModel):
    __tablename__ = 'maintenance'

    company_id = Column(ForeignKey('company.id'))
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    turbine = Column(String(25), nullable=False, index=True)
    component = Column(String(60), nullable=False, index=True)
    reason = Column(Text)
    note = Column(Text)

    @classmethod
    def get_for_company_id(cls, company_id):
        return cls.query.filter(cls.company_id == company_id).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).one_or_none(    )
