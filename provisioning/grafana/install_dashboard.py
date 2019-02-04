import json
import os
import logging
import yaml

import requests

from helpers import (
    switch_organisation_for_user,
    build_api_http,
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

CURRENT_DIR = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO)


request_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

logging.info(f"Get Organisation Id for {ADS_DEFAULT_COMPANY_NAME}")
get_organisation_response = requests.get(
    api_url + f"/orgs/name/{ADS_DEFAULT_COMPANY_NAME}",
    headers=request_headers
)
organisation_id = get_organisation_response.json().get('id')


switch_organisation_for_user(GRAFANA_DEFAULT_USER_ID, organisation_id, request_headers, api_url)


logging.info(f"Install Dashboard {ADS_DEFAULT_COMPANY_NAME}")

dashboard = json.load(open(os.path.join(CURRENT_DIR, 'resources', 'dashboard.json')))


add_datasource_response = requests.post(
    api_url + '/dashboards/db',
    headers=request_headers,
    json={
        "dashboard": dashboard,
        "overwrite": True,
        "folderId": 0
    }
)


switch_organisation_for_user(GRAFANA_DEFAULT_USER_ID, GRAFANA_DEFAULT_ORG_ID, request_headers, api_url)
