import os
import logging

import requests

logging.basicConfig(level=logging.INFO)

ADS_ADMIN_USERNAME = os.environ.get('ADS_ADMIN_USERNAME')
ADS_ADMIN_PASSWORD = os.environ.get('ADS_ADMIN_PASSWORD')
ADS_ADMIN_DOMAIN = os.environ.get('ADS_ADMIN_DOMAIN')

ADS_DEFAULT_COMPANY_NAME = os.environ.get('ADS_DEFAULT_COMPANY_NAME')
ADS_DEFAULT_COMPANY_DOMAIN = os.environ.get('ADS_DEFAULT_COMPANY_DOMAIN')
ADS_DEFAULT_GRAFANA_USERNAME = os.environ.get('ADS_DEFAULT_GRAFANA_USERNAME')
ADS_DEFAULT_EMAIL = os.environ.get('ADS_DEFAULT_EMAIL')
ADS_DEFAULT_PASSWORD = os.environ.get('ADS_DEFAULT_PASSWORD')


APP_URL = 'http://localhost:5000/{}'

request_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# login superuser
logging.info("Login Superuser to retrieve Token")

admin_email = "{}@{}".format(ADS_ADMIN_USERNAME, ADS_ADMIN_DOMAIN)

response = requests.post(
    APP_URL.format('auth/login'),
    json={"email": admin_email, "password": ADS_ADMIN_PASSWORD},
    headers=request_headers
)

admin_token = response.json().get('token')

request_headers.update({'X-Token': admin_token})

logging.info(f"Register default company {ADS_DEFAULT_COMPANY_NAME}")

# register_company
response = requests.post(
    APP_URL.format('company/register'),
    json={"name": ADS_DEFAULT_COMPANY_NAME, "domain": ADS_DEFAULT_COMPANY_DOMAIN},
    headers=request_headers
)

response_body = response.json()
company_id = response_body.get("id")

company_configuration = {
    'grafana_user_id': ADS_DEFAULT_GRAFANA_USERNAME
}

logging.info(f"Update configuration for company name {ADS_DEFAULT_COMPANY_NAME}")
response = requests.post(
            APP_URL.format(f'/configuration/{company_id}'),  # company 1 is the super-company...
            json=company_configuration,
            headers=request_headers
        )

logging.info(f"Create User name {ADS_DEFAULT_EMAIL}")
create_user_response = requests.post(
    APP_URL.format('user/register'),
    headers=request_headers,
    json={"email": ADS_DEFAULT_EMAIL, "password": ADS_DEFAULT_PASSWORD}
)

confirmation_token = create_user_response.json().get('confirmation_token')

confirm_user_response = requests.get(
    APP_URL.format(f'user/confirm/{confirmation_token}'),
    headers=request_headers
)
