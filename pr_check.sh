#!/bin/bash
set -xvo pipefail

# This script performs a build of the Dockerfile.ci image which performs type checking and linting
# This is followed by an integration test of the application using a Postgres DB that is spun up with
# Podman. The reason I'm using these raw podman commands rather than podman-compose is due to limitations
# in Podman compose, specifically that the `depends_on` healthcheck feature isn't supported
# (see: https://github.com/containers/podman-compose/issues/866)
# once the DB & web-app are spun up, several queries are run to validate the DB functionality
# and finally everything is torn down in the end

# $1: api_type
# $2: web app port
test_data() {
    TOKEN=$(curl --silent http://localhost:$2/api/v1/token?scope=$1 | sed 's/"//g')
    POST_RES=$(curl --silent -X POST --header "Content-Type: application/json" --header "X-Auth: $TOKEN" --data @examples/$1.json http://localhost:$2/api/v1/$1/app-sre-prod-01)
    if [[ ! $POST_RES =~ "ok" ]]; then
        echo "test of $1 api failed, returning '$POST_RES' when 'ok' was expected"
        RETURN=1
    fi
    curl --silent --request DELETE "http://localhost:$2/api/v1/token/$TOKEN?scope=$1"
}

make ci
RETURN=$?

IP=$(hostname -I | tr -d '[:blank:]')

DB_CONTAINER=dashdotdb-pg
APP_CONTAINER=dashdotdb-app

podman run --rm -d -e POSTGRESQL_PASSWORD=postgres -e POSTGRESQL_USER=dashdotdb -e POSTGRESQL_DATABASE=dashdotdb --health-cmd "pg_isready -U dashdotdb -d dashdotdb" --name dashdotdb-pg -p 5432 registry.redhat.io/rhel9/postgresql-15
podman wait --condition=healthy $DB_CONTAINER
PG_PORT=$(podman port "${DB_CONTAINER}" | awk -F: '{print $2}')

podman run --rm -d -e DASHDOTDB_DATABASE_URL=postgresql://dashdotdb:postgres@$IP:$PG_PORT/dashdotdb -p 8080 --health-cmd "curl -f http://localhost:8080/api/healthz/ready" --name $APP_CONTAINER app-sre-dashdotdb:do-not-use
podman wait --condition=healthy $APP_CONTAINER


WEB_PORT=$(podman port "${APP_CONTAINER}" | awk -F: '{print $2}')

test_data imagemanifestvuln "$WEB_PORT"
test_data serviceslometrics "$WEB_PORT"
test_data deploymentvalidation "$WEB_PORT"

podman stop $APP_CONTAINER $DB_CONTAINER

exit $RETURN
