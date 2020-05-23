# Dash.DB

AppSRE Dashboards Database: a repository of metrics and statistics about the services we run.

# Quickstart

Run a PostgreSQL instance:

```
$ docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
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

# Stored Procedures

The CLI uses SQLAlchemy to interact with the Database, but Grafana Dashboards will directly access PostgreSQL
instance to query data from. Because those queries can be complex, we create stored procedures to simplify the
execution of those queries.

The stored procedures can be found here: [dashdotdb/db/stored_procedures.py](dashdotdb/db/stored_procedures.py)

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

# Database Model

The current Entity Relationship Diagram looks like this:

![](docs/dashdotdb.png)

To change the database, start by editing the [ERD ".dia" file](/docs/dashdotdb.dia) using
[Gnome Dia](https://wiki.gnome.org/Apps/Dia/).

Then reflect the changes to the ERD in the database model:
[dashdotdb/db/model.py](/dashdotdb/db/model.py).

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

At the moment, there's no upgrade strategy. In the future, database upgrades shall be implemented
using [Alembic](https://alembic.sqlalchemy.org/).

# Extending the CLI

The `dashdotdb` Command Line Interface is pluggable and easily extensible. It is composed of three
parts:

```
$ dashdotdb apply imagemanifestvuln -c cluster-01 -f manifest.json
              │           │         │                             │
              │           │         └────── PLUGIN OPTIONS ───────┘
              │           │
              │           └── PLUGIN
              │
              └── ACTION
```

To create a new plugin, first you have to create a new Python file in the
[plugins directory](dashdotdb/cli/plugins/):

```python
from dashdotdb.cli.plugins_interface import Cmd


class Dummy(Cmd):

    description = 'Dummy Plugin for Demonstration'

    def configure_apply(self, parser):
        parser = super().configure_apply(parser)
        parser.add_argument('-o', '--option', type=str,
                            required=True, help='dummy apply option')

    def configure_get(self, parser):
        parser = super().configure_get(parser)
        parser.add_argument('-d', '--debug', type=str,
                            help='dummy get option')

    def apply(self, args):
        self.log.info('Applying!')

    def get(self, args):
        self.log.info('Getting!')
```

Then, you have to add your new plugin to the [setup.py](setup.py):

```
            'plugins': [
                  'imagemanifestvuln = dashdotdb.cli.plugins.imagemanifestvuln:ImageManifestVuln',
                  'dummy = dashdotdb.cli.plugins.dummy:Dummy',
            ]
```

And last but not lease, you have to (re)install the Python package:

```
$ python setup.py develop
```

Checking the `apply` help:

```
$ dashdotdb apply -h
usage: dashdotdb apply [-h] {dummy,imagemanifestvuln} ...

optional arguments:
  -h, --help            show this help message and exit

plugins:
  {dummy,imagemanifestvuln}
                        help
    dummy               Dummy Plugin for Demonstration
    imagemanifestvuln   Image Manifest Vulnerability

```

Checking the `apply dummy` help:

```
$ dashdotdb apply dummy -h
usage: dashdotdb apply dummy [-h] -o OPTION

optional arguments:
  -h, --help            show this help message and exit
  -o OPTION, --option OPTION
                        dummy apply option
```

Running:

```
$ dashdotdb apply dummy -o foo
Applying!
```

```
$ dashdotdb get dummy -d bar
Getting!
```

# Accessing the Database

Using the `dummy` plugin we created in the previous step, let's run a simple query:

```python
from tabulate import tabulate

from dashdotdb import Session
from dashdotdb import Pod

from dashdotdb.cli.plugins_interface import Cmd


class Dummy(Cmd):

    description = 'Dummy Plugin for Demonstration'

    def configure_apply(self, parser):
        parser = super().configure_apply(parser)
        parser.add_argument('-o', '--option', type=str,
                            required=True, help='dummy apply option')

    def configure_get(self, parser):
        parser = super().configure_get(parser)
        parser.add_argument('-d', '--debug', type=str,
                            help='dummy get option')

    def apply(self, args):
        self.log.info('Applying!')

    def get(self, args):
        pods = Session.query(Pod).distinct(Pod.name)
        result = {'PODS': [pod.name for pod in pods]}
        self.log.info(tabulate(result, headers=result.keys()))
```

Running:

```
$ dashdotdb get dummy
PODS
---------------------------
cso/sleep2-65844c6b58-2q2s5
cso/sleep2-65844c6b58-qlng8
cso/sleep-6f84df5847-4bn9p
cso/sleep-6f84df5847-bctxz
cso/sleep-6f84df5847-dh9l8
```
