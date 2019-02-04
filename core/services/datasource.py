import os
from typing import List

import pandas
from sqlalchemy.orm import Query

from core.models.customer import User
from core.models.datasource import DataSource, UploadTypes, DataSourceConfiguration
from core.services.upload.base import AbstractUploadManager


def get_by_upload_code(upload_code: str) -> DataSource:
    return DataSource.get_by_upload_code(upload_code)


def datasource_name_exists(datasource_name: str) -> bool:
    count = DataSource.query.filter(DataSource.name == datasource_name).count()
    if count > 0:
        return True
    return False


def generate_filename(upload_code: str, filename: str) -> str:
    return DataSource.generate_filename(upload_code, filename)


def insert(upload: DataSource):
    upload.save()
    return upload


def delete(datasource: DataSource):
    datasource.delete()


def get_dataframe(datasource: DataSource) -> pandas.DataFrame:
    datasource = DataSource.get_by_upload_code(datasource.upload_code)
    return datasource.get_file()


def get_configuration_by_id(id: int) -> DataSourceConfiguration:
    return DataSourceConfiguration.get_for_id(id)


def get_configuration_by_company_id(company_id: int) -> List[DataSourceConfiguration]:
    return DataSourceConfiguration.get_for_company_id(company_id).all()


def save_datasource(name: str, company_id: int, datasource_configuration_id: int, upload_code: str,
                    upload_manager: AbstractUploadManager, uploaded_dataframe: pandas.DataFrame, user: User):
    datasource_configuration = get_configuration_by_id(datasource_configuration_id)
    if not datasource_configuration:
        raise Exception(f"No datasource configuration available for {datasource_configuration_id}")
    saved_path = upload_manager.store(uploaded_dataframe, company_id, upload_code)

    upload = DataSource(
        user_id=user.id,
        name=name,
        datasource_configuration_id=datasource_configuration.id,
        company_id=user.company_id,
        upload_code=upload_code,
        type=UploadTypes.FILESYSTEM,
        filename=os.path.basename(saved_path),
        meta=datasource_configuration.meta
    )

    datasource = insert(upload)
    return datasource


def filter_by_company_id(query: Query, company_id: int) -> Query:
    return query.filter(DataSource.company_id == company_id).order_by(DataSource.created_at.desc())


def filter_by_datasource_configuration_id(query: Query, datasource_configuration_id: int) -> Query:
    return query.filter(DataSource.datasource_configuration_id == datasource_configuration_id)


def filter_by_label(query: Query, label: str) -> Query:
    return query.filter(DataSource.label == label)
