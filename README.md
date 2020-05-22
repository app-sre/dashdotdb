# Dash.DB

AppSRE Dashboards Database: a repository of metrics and statistics abput the services we run.

# Quickstart

Run a PostgreSQL instance:

```
docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
```

Export the `DASHDOTDB_DATABASE_URL`:

```
$ export DASHDOTDB_DATABASE_URL=postgres://postgres:postgres@127.0.0.1:5432/postgres
```

Install the package:

```
$ python -m venv venv
$ source venv/bin/activate
$ python setup.py develop
```

Initialize the Database:

```
$ dashdotdb-admin resetdb
(re)Creating tables
(re)Creating stored procedures
```

Apply `imagemanifestvuln` example data:

```
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

```
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

# Entity Relashioship Diagram

![](docs/dashdotdb.png)
