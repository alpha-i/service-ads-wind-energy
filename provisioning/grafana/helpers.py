import logging

import requests

GRAFANA_DEFAULT_ORG_ID = 1
GRAFANA_DEFAULT_USER_ID = 1

def build_api_http(username, password):
    return f'http://{username}:{password}@localhost:3000/api'


def switch_organisation_for_user(user_id, destination_org, headers, api_http):

    logging.info(f"Switch admin to {destination_org} organisation")
    requests.post(
        api_http + f"/users/{user_id}/using/{destination_org}",
        headers=headers
    )
