from core.models.customer import Company, CompanyConfiguration


def get_for_email(email: str):
    company = Company.get_for_email(email)
    return company


def get_for_domain(domain: str):
    company = Company.get_for_domain(domain)
    return company


def get_by_id(company_id: int):
    company = Company.get_by_id(company_id)
    return company


def insert(company: Company):
    company.save()
    return company


def get_configurations_by_company_id(id: int):
    return CompanyConfiguration.get_by_company_id(id)


def insert_configuration(company_configuration: CompanyConfiguration):
    company_configuration.save()
    return company_configuration


def get_datasource_interpreter(company_configuration: CompanyConfiguration):
    from core.interpreters import datasource
    interpeter = getattr(datasource, company_configuration.configuration['datasource_interpreter'])
    return interpeter()


def get_upload_manager(company_configuration: CompanyConfiguration):
    from core.services import upload
    upload_manager = getattr(upload, company_configuration.configuration['upload_manager'])
    return upload_manager(company_configuration)
