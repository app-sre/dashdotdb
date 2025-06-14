# Dash.DB

The AppSRE Dashboards Database is a repository of metrics and statistics about
the services we run.

The Dash.DB is a service created to implement the Database Model and to
read/write data from/to the Database.

It's a building block - and a central part - in the architecture created to
extract information from multiples sources, place them into the Database and
expose the relevant insights via Grafana Dashboards and monthly reports.

## Quickstart

### Docker-compose

You can quickly run the app locally with docker-compose

```shell
docker-compose up
```

Test data can be generated via

```shell
make test-data
```

### Manual

Run a PostgreSQL instance:

```shell
# using default settings
make db-up

# or, by hand
docker run -d --rm --name dashdot-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres

# optional: tail -f database logs
docker logs dashdot-postgres -f
```

Open a new terminal. Install the package:

```shell
uv sync --group dev
```

Export the `FLASK_APP` and `DASHDOTDB_DATABASE_URL` so Flask knows where to find the `dashdotdb` source code, and how to connect to the database:

```shell
export FLASK_APP=dashdotdb
export DASHDOTDB_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres
```

Initialize the Database using default settings. `DASHDOTDB_DATABASE_URL` can be changed, if necessary.

```shell
make db-init
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> c4f641d56546, Initial migration.
```

With a custom `DASHDOTDB_DATABASE_URL`:

```shell
make DASHDOTDB_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres db-init
```

Run the service:

```shell
# requires FLASK_APP and DASHDOTDB_DATABASE_URL environment variables set
uv run --group dev flask run --debugger --port 8080
```

## Using the app

Open a new terminal. Get a token:

```shell
TOKEN=$(curl --silent localhost:8080/api/v1/token?scope=imagemanifestvuln | sed 's/"//g')
```

Apply `imagemanifestvuln` example data:

```shell
$ curl --request POST \
--header "Content-Type: application/json" \
--header "X-Auth: $TOKEN" \
--data @examples/imagemanifestvuln.json \
localhost:8080/api/v1/imagemanifestvuln/app-sre-prod-01
```

Or, if you already have a live cluster:

```shell
$ oc get imagemanifestvuln <object_name> -o json | $ curl --request POST \
--header "Content-Type: application/json" \
--header "X-Auth: $TOKEN" \
--data @- \
"localhost:8080/api/v1/imagemanifestvuln/app-sre-prod-01"
...
```

(Note: Data that is uploaded to dashdotDB is not actually available for query until the token that was used to upload it is deleted. The only data available for query at any given moment is that which was uploaded using the most recently deleted token.)

Close the token (to make the latest data queryable):

```shell
curl --request DELETE "localhost:8080/api/v1/token/$TOKEN?scope=imagemanifestvuln"
```

Query vulnerabilities:

```shell
$ curl "localhost:8080/api/v1/imagemanifestvuln?cluster=app-sre-prod-01&namespace=cso"
[
  {
    "affected_pods": 3,
    "current_version": "9.0.3-15.el8",
    "fixed_in_version": "0:9.0.3-16.el8",
    "link": "https://access.redhat.com/errata/RHSA-2020:1916",
    "manifest": "sha256:9e0c275",
    "name": "centos:8",
    "package": "platform-python-pip",
    "repository": "quay.io/app-sre/centos",
    "severity": "Medium",
    "vulnerability": "RHSA-2020:1916"
  },
  {
    "affected_pods": 3,
    "current_version": "8.3.1-4.5.el8",
    "fixed_in_version": "0:8.3.1-5.el8",
    "link": "https://access.redhat.com/errata/RHSA-2020:1864",
    "manifest": "sha256:9e0c275",
    "name": "centos:8",
    "package": "libstdc++",
    "repository": "quay.io/app-sre/centos",
    "severity": "Medium",
    "vulnerability": "RHSA-2020:1864"
  },
...
```

Prometheus metrics endpoint:

```shell
$ curl "localhost:8080/api/v1/imagemanifestvuln/metrics"
...
# HELP imagemanifestvuln_total Vulnerabilities total per severity
# TYPE imagemanifestvuln_total counter
imagemanifestvuln_total{cluster="app-sre-prod-01",namespace="cso",severity="Medium"} 86.0
imagemanifestvuln_total{cluster="app-sre-prod-01",namespace="cso",severity="High"} 43.0
imagemanifestvuln_total{cluster="app-sre-prod-01",namespace="cso",severity="Low"} 20.0
imagemanifestvuln_total{cluster="app-sre-prod-01",namespace="cso",severity="Unknown"} 5.0
imagemanifestvuln_total{cluster="app-sre-prod-01",namespace="cso",severity="Critical"} 4.0
...
```

## Changing the Database Model

The current Entity Relationship Diagram looks like this:

![Current entity relationship diagram for dashdotdb. It depicts an UML diagram that outlines the complex model relationships for dashdotdb](docs/dashdotdb.png)

### ERD

To change the database, start by editing the
[ERD ".dia" file](/docs/dashdotdb.dia) using
[Gnome Dia](https://wiki.gnome.org/Apps/Dia/).

The Dia application is known to have issues running on Mac OS. It may launch fine the first time, and then never again. Following [these directions](https://apple.stackexchange.com/a/411620) should help fix that.

### Model

Reflect the changes to the ERD in the database model, either by updating an
existing model or by creating new ones. Models are placed
[in /dashdotdb/models](/dashdotdb/models/).

### DB Upgrade

Create the upgrade routine executing the command:

```shell
make db
```

That will create a new migration file in the
[migrations](/migrations/versions/) directory.

NOTE: Any change to a Enum type will need to be done manually.  See
this [issue](https://github.com/sqlalchemy/alembic/issues/278) and an
[example](https://markrailton.com/blog/creating-migrations-when-changing-an-enum-in-python-using-sql-alchemy).

For the deployed environments, the [entrypoint.sh](entrypoint.sh) will
execute the migration before running the service. To execute the migration
on your own database instance, run:

```shell
FLASK_APP=dashdotdb uv run --group dev flask db upgrade
```

### SQLAlchemy Debug

To enable verbose SQLAlchemy logging, which will output the compiled queries
add to the app.config object:

```python
app.config['SQLALCHEMY_ECHO'] = True
```
