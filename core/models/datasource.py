import enum
import os

import pandas as pd
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, JSON, UniqueConstraint
from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from config import HDF5_STORE_INDEX, UPLOAD_ROOT_FOLDER
from core.database import local_session_scope
from core.models.base import BaseModel
from core.models.customer import CustomerAction, Actions


class UploadTypes(enum.Enum):
    FILESYSTEM = 'filesystem'
    BLOBSTORE = 'blobstore'


class LabelTypes(enum.Enum):
    NORMAL = 'normal'
    ABNORMAL = 'abnormal'


class DataSourceConfiguration(BaseModel):
    __tablename__ = 'data_source_configuration'
    __table_args__ = (UniqueConstraint('company_id', 'name', name='_datasource_config_name_company_uc'),)

    company_id = Column(ForeignKey('company.id', name='data_source_company_id_fk'))
    company = relationship('Company', foreign_keys=company_id)

    name = Column(String(60), index=True, nullable=False)
    meta = Column(JSON)

    @classmethod
    def get_for_company_id(cls, company_id):
        return cls.query.filter(cls.company_id == company_id)

    @classmethod
    def get_for_id(cls, id):
        return cls.query.filter(cls.id == id).one_or_none()


class DataSource(BaseModel):
    INCLUDE_ATTRIBUTES = ('type', 'meta', 'location', 'datasource_configuration', 'is_part_of_training_set')

    __tablename__ = 'data_source'
    __table_args__ = (UniqueConstraint('company_id', 'name', name='_datasource_company_id_name_uc'),)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=user_id)

    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship('Company', foreign_keys=company_id)

    datasource_configuration_id = Column(
        ForeignKey('data_source_configuration.id',
                   name='data_source_datasource_configuration_id_fkey')
    )
    datasource_configuration = relationship(
        'DataSourceConfiguration', foreign_keys=datasource_configuration_id
    )

    label = Column(Enum(LabelTypes), index=True, nullable=True)  # is null until someone flags it explicitly
    name = Column(String(), index=True)
    upload_code = Column(String(), index=True)
    type = Column(Enum(UploadTypes), index=True)
    filename = Column(String(), nullable=False)
    meta = Column(JSON)

    @property
    def location(self):
        return os.path.join(UPLOAD_ROOT_FOLDER, str(self.company_id), self.filename)

    def get_file(self):
        with pd.HDFStore(self.location) as hdf_store:
            dataframe = hdf_store[HDF5_STORE_INDEX]
            return dataframe

    @staticmethod
    def get_for_user(user_id):
        return DataSource.query.filter(DataSource.user_id == str(user_id)).all()

    @staticmethod
    def get_by_upload_code(upload_code):
        try:
            return DataSource.query.filter(DataSource.upload_code == upload_code).one()
        except NoResultFound:
            return None

    @staticmethod
    def generate_filename(upload_code, original_filename):
        return f"{upload_code}_{original_filename}"

    @staticmethod
    def get_for_datasource_configuration(datasource_configuration):
        return DataSource.query.filter(
            DataSource.datasource_configuration_id == datasource_configuration.id,
            DataSource.label == LabelTypes.NORMAL
        ).all()


def update_user_action(mapper, connection, self):
    action = CustomerAction(
        company_id=self.company_id,
        user_id=self.user_id,
        action=Actions.FILE_UPLOAD
    )
    with local_session_scope() as session:
        session.add(action)


event.listen(DataSource, 'after_insert', update_user_action)
