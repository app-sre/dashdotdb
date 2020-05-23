# Dash.DB

AppSRE Dashboards Database: a repository of metrics and statistics about the services we run.

# Quickstart

Run a PostgreSQL instance:

```shell script
$ docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
```

Export the `DASHDOTDB_DATABASE_URL`:

```shell script
$ export DASHDOTDB_DATABASE_URL=postgres://postgres:postgres@127.0.0.1:5432/postgres
```

Install the package:

```shell script
$ python -m venv venv
$ source venv/bin/activate
$ python setup.py develop
```

Initialize the Database:

```shell script
$ dashdotdb-admin resetdb
(re)Creating tables
(re)Creating stored procedures
```

Apply `imagemanifestvuln` example data:

```shell script
$ dashdotdb apply imagemanifestvuln -c cluster-01 -f examples/imagemanifestvuln.json
token created
cluster cluster-01 created
namespace cso created
image quay.io/app-sre/centos created
feature platform-python-pip created
severity Medium created
vulnerability RHSA-2020:1916 created
...
```

Query vulnerabilities:

```shell script
$ dashdotdb get imagemanifestvuln -c cluster-01 -n cso -s High
REPOSITORY              NAME      MANIFEST          AFFECTED_PODS  VULNERABILITY    SEVERITY    PACKAGE                   CURRENT_VERSION    FIXED_IN_VERSION     LINK
----------------------  --------  --------------  ---------------  ---------------  ----------  ------------------------  -----------------  -------------------  -----------------------------------------------
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0273   High        sqlite-libs               3.26.0-3.el8       0:3.26.0-4.el8_1     https://access.redhat.com/errata/RHSA-2020:0273
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0229   High        sqlite-libs               3.26.0-3.el8       0:3.26.0-4.el8_0     https://access.redhat.com/errata/RHSA-2020:0229
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0575   High        systemd-udev              239-18.el8_1.1     0:239-18.el8_1.4     https://access.redhat.com/errata/RHSA-2020:0575
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0575   High        systemd-libs              239-18.el8_1.1     0:239-18.el8_1.4     https://access.redhat.com/errata/RHSA-2020:0575
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0575   High        systemd                   239-18.el8_1.1     0:239-18.el8_1.4     https://access.redhat.com/errata/RHSA-2020:0575
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0271   High        libarchive                3.3.2-7.el8        0:3.3.2-8.el8_1      https://access.redhat.com/errata/RHSA-2020:0271
quay.io/app-sre/centos  centos:8  sha256:9e0c275                3  RHSA-2020:0575   High        systemd-pam               239-18.el8_1.1     0:239-18.el8_1.4     https://access.redhat.com/errata/RHSA-2020:0575
quay.io/app-sre/centos  centos:7  sha256:a42f741                2  RHSA-2018:1700   High        procps-ng                 3.3.10-10.el7      0:3.3.10-17.el7_5.2  https://access.redhat.com/errata/RHSA-2018:1700
quay.io/app-sre/centos  centos:7  sha256:a42f741                2  RHSA-2019:0368   High        systemd-libs              219-30.el7_3.6     0:219-62.el7_6.5     https://access.redhat.com/errata/RHSA-2019:0368
...
```

# Stored Procedures

The CLI uses SQLAlchemy to interact with the Database, but Grafana Dashboards will directly access PostgreSQL
instance to query data from. Because those queries can be complex, we create stored procedures to simplify the
execution of those queries.

The stored procedures may be found here: [dashdotdb/db/stored_procedures.py](dashdotdb/db/stored_procedures.py)

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

# Entity Relationship Diagram

![](docs/dashdotdb.png)
