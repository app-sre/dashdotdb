# Dash.DB

The AppSRE Dashboards Database is a repository of metrics and statistics about
the services we run.

The Dash.DB is a service created to implement the Database Model and to
read/write data from/to the Database.

It's a building block - and a central part - in the architecture created to
extract information from multiples sources, place them into the Database and
expose the relevant insights via Grafana Dashboards and monthly reports.

# Quickstart

Run a PostgreSQL instance:

```
$ docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
```

Open a new terminal. Install the package:

```
$ python -m venv venv
$ source venv/bin/activate
$ python setup.py develop
```

Export the `FLASK_APP` and the `DASHDOTDB_DATABASE_URL`:

```
$ export FLASK_APP=dashdotdb
$ export DASHDOTDB_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres
```

Initialize the Database:

```
$ FLASK_APP=dashdotdb flask db upgrade
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> c4f641d56546, Initial migration.
```

Run the service:

```
$ flask run --debugger --port 8080
```

Open a new terminal. Apply `imagemanifestvuln` example data:

```
$ curl --request POST \
--header "Content-Type: application/json" \
--data @examples/imagemanifestvuln.json \
localhost:8080/api/v1/imagemanifestvuln/app-sre-prod-01
```

Or, if you already have a live cluster:

```
$ oc get imagemanifestvuln <object_name> -o json | $ curl --request POST \
--header "Content-Type: application/json" \
--data @- \
"localhost:8080/api/v1/imagemanifestvuln/app-sre-prod-01"
...
```

Query vulnerabilities:

```
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

```
$ curl "localhost:8080/api/v1/metrics"
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

# Changing the Database Model

The current Entity Relationship Diagram looks like this:

![](docs/dashdotdb.png)

## ERD

To change the database, start by editing the
[ERD ".dia" file](/docs/dashdotdb.dia) using
[Gnome Dia](https://wiki.gnome.org/Apps/Dia/).

## Model

Reflect the changes to the ERD in the database model, either by updating an
existing model or by creating new ones. Models are placed
[here](/dashdotdb/models/).

## DB Upgrade

Create the upgrade routine executing the command:

```
$ FLASK_APP=dashdotdb flask db migrate
```

That will create a new migration file in the
[migrations](/migrations/versions/) directory.

For the deployed environments, the [entrypoint.sh](entrypoint.sh) will
execute the migration before running the service. To execute the migration
on your own database instance, run:

```
FLASK_APP=dashdotdb flask db upgrade
```

## SQLAlchemy Debug
To enable verbose SQLAlchemy logging, which will output the compiled queries 
add to the app.config object:
```
app.config['SQLALCHEMY_ECHO'] = True
```
