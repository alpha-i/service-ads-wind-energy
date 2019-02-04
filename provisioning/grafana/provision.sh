#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

set -a
. ${CURRENT_DIR}/../build.env
set +a

python ${CURRENT_DIR}/create_user.py
python ${CURRENT_DIR}/install_datasource.py
python ${CURRENT_DIR}/install_dashboard.py

