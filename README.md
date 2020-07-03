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
$ docker run --rm --it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
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
$ export DASHDOTDB_DATABASE_URL=postgres://postgres:postgres@127.0.0.1:5432/postgres
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
$ oc get imagemanifestvuln --all-namespaces -o json | $ curl --request POST \
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

To change the database, start by editing the
[ERD ".dia" file](/docs/dashdotdb.dia) using
[Gnome Dia](https://wiki.gnome.org/Apps/Dia/).

Then reflect the changes to the ERD in the database model:
[dashdotdb/db/model.py](/dashdotdb/models/imagemanifestvuln.py).

Last but not least, apply your changes to the database using:

```
$ dashdotdb-admin initdb
```

This will create all new tables defined in the Model.

Alternatively, you might want to use:

```
$ dashdotdb-admin resetdb
```

This will remove all the tables and recreate them according to the Model.

At the moment, there's no upgrade strategy. In the future, database upgrades
shall be implemented using [Alembic](https://alembic.sqlalchemy.org/).

# Stored Procedures

The CLI uses SQLAlchemy to interact with the Database, but Grafana Dashboards
will directly access PostgreSQL instance to query data from. Because those
queries can be complex, we create stored procedures to simplify the execution
of them.

The stored procedures can be found here:
[dashdotdb/db/stored_procedures.py](dashdotdb/storedprocedures/imagemanifestvuln.py)

## Examples

To create this gauge:

![](docs/grafana1.png)

We can use this query:

```sql
SELECT now() AS time,
       count(feature) as value,
       severity as metric
FROM get_severity_count('$cluster','$namespace', 'High')
GROUP BY severity;
```

To create this table:

![](docs/grafana2.png)

We can use this query:

```sql
SELECT * FROM get_vulnerabilities('$cluster','$namespace');
```
