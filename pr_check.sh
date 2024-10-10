#!/bin/bash

set -exvo pipefail


# $1: api_type
test_data() {
    TOKEN=$(curl --silent localhost:8080/api/v1/token?scope=$1 | sed 's/"//g')
    POST_RES=$(curl -X POST --header "Content-Type: application/json" --header "X-Auth: $TOKEN" --data @examples/$1.json localhost:8080/api/v1/$1/app-sre-prod-01)
    if [[ ! $POST_RES =~ "ok" ]]; then
        echo "test of $1 api failed, returning '$POST_RES' when 'ok' was expected"
        exit 1
    fi
    curl --request DELETE "localhost:8080/api/v1/token/$TOKEN?scope=$1"
} 

make ci

# now run some checks against test data
podman-compose up -d

# https://github.com/containers/podman-compose/issues/710
# --wait not supported in podman compose yet
sleep 10

test_data imagemanifestvuln
test_data serviceslometrics
test_data deploymentvalidation

podman-compose down
