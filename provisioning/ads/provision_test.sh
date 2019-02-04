#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

set -a
. ${CURRENT_DIR}/../build.env
set +a

export APP_CONFIG=environments/test.env
export FLASK_APP=application.py

flask create_superuser ${ADS_ADMIN_USERNAME} ${ADS_ADMIN_PASSWORD}

python ${CURRENT_DIR}/create_user.py

