import os
import logging

import requests

from helpers import (
    switch_organisation_for_user, build_api_http,
    GRAFANA_DEFAULT_ORG_ID,
    GRAFANA_DEFAULT_USER_ID
)


GF_SECURITY_ADMIN_PASSWORD = os.environ.get('GF_SECURITY_ADMIN_PASSWORD')
GRAFANA_ADMIN_USERNAME = os.environ.get('GRAFANA_ADMIN_USERNAME')
GRAFANA_USER_PASSWORD = os.environ.get('GRAFANA_USER_PASSWORD')
ADS_DEFAULT_COMPANY_NAME = os.environ.get('ADS_DEFAULT_COMPANY_NAME')
ADS_ADMIN_DOMAIN = os.environ.get('ADS_ADMIN_DOMAIN')
ADS_DEFAULT_GRAFANA_USERNAME = os.environ.get('ADS_DEFAULT_GRAFANA_USERNAME')


api_url = build_api_http(GRAFANA_ADMIN_USERNAME, GF_SECURITY_ADMIN_PASSWORD)


logging.basicConfig(level=logging.INFO)


request_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

logging.info(f"Create Organisation {ADS_DEFAULT_COMPANY_NAME}")
# create organisation
response = requests.post(
    api_url + "/orgs",
    json={"name": ADS_DEFAULT_COMPANY_NAME},
    headers=request_headers
)

organisation_id = response.json().get('orgId')

switch_organisation_for_user(GRAFANA_DEFAULT_USER_ID, organisation_id, request_headers, api_url)

# create user
logging.info(f"Create User {ADS_DEFAULT_GRAFANA_USERNAME}")
response = requests.post(
    api_url + "/admin/users",
    headers=request_headers,
    json={
        "name": "User",
        "email": "{}@{}".format(ADS_DEFAULT_GRAFANA_USERNAME, ADS_ADMIN_DOMAIN),
        "login": ADS_DEFAULT_GRAFANA_USERNAME,
        "password": GRAFANA_USER_PASSWORD
    }
)

user_id = response.json().get('id')


logging.info(f"Add User {ADS_DEFAULT_GRAFANA_USERNAME} to organisation {ADS_DEFAULT_COMPANY_NAME} id {organisation_id}")
add_user_to_org_response = requests.post(
    api_url + f"/orgs/{organisation_id}/users",
    headers=request_headers,
    json={
      "loginOrEmail": ADS_DEFAULT_GRAFANA_USERNAME,
      "role": "Viewer"
    }
)

logging.info(f"Remove User {ADS_DEFAULT_GRAFANA_USERNAME} from default organisation {GRAFANA_DEFAULT_ORG_ID}")
remove_user_to_org_response = requests.delete(
    api_url + f"/orgs/{GRAFANA_DEFAULT_ORG_ID}/users/{user_id}",
    headers=request_headers
)

switch_organisation_for_user(GRAFANA_DEFAULT_USER_ID, GRAFANA_DEFAULT_ORG_ID, request_headers, api_url)
