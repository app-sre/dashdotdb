# Multi SLO Doc Support

## Date of Proposal

August 19, 2021

## Tracking

Implementation is tracked through [this Jira ticket](https://issues.redhat.com/browse/APPSRE-3570).

## Context

Part of the onboarding process for services within Red Hat's App-SRE organization involves creating SLO documents. [Here](https://gitlab.cee.redhat.com/service/app-interface/-/tree/master/data/services/ocm/slo-documents), for example, are the 'ocm' service's SLO documents.

[Every 24 hours](https://github.com/app-sre/qontract-reconcile/blob/7f50680e999d99b80ffe693cad014838f3d53cb6/helm/qontract-reconcile/values-internal.yaml#L400-L412) SLO data [is uploaded to dashdotDB](https://github.com/app-sre/qontract-reconcile/blob/7f50680e999d99b80ffe693cad014838f3d53cb6/openshift/qontract-reconcile-internal.yaml#L7817-L7878) by executing [this code](https://github.com/app-sre/qontract-reconcile/blob/dafaa105b7ef9e7989760586d1d73acfa6d8cf92/reconcile/dashdotdb_slo.py#L35-L61).

[At the begining of every month](https://gitlab.cee.redhat.com/service/app-interface/-/blob/c6445087cf496a32569ab77a5eaf480d1ab02647/data/services/app-interface/cicd/ci-int/jobs.yaml#L51-56) the [app-interface-reporter process](https://github.com/app-sre/qontract-reconcile/blob/572dc43d79c53ed24b99c0c7d109bb55be6cf49c/tools/app_interface_reporter.py) pulls SLO data on all services from dash.db in order to produce a monthly report. [Here](https://gitlab.cee.redhat.com/service/app-interface/-/blob/074885d030d33977f1169846abf4e53f6a168bd1/data/reports/ocm/2021-08-01.yml#L128-143), for example, is the SLO data of one of the 'ocm' service's reports.

Visual-Qontract can then [use the SLO data from these reports](https://github.com/app-sre/visual-qontract/blob/bb5e993a428780ccd6a1d4208b36740e46d96f79/src/pages/elements/Report.js#L546-L625) to produce a visual table within a [visual report page](https://visual-app-interface.devshift.net/reports#/reports/ocm/2021-08-01.yml).

More on App-SRE SLO architecture can be seen [here](https://docs.google.com/presentation/d/1W6DeV6YXuDDLgVdMwna0VMPyrZgBUvf6oHWBz4-MJm4/edit#slide=id.ge7fa02b0e0_0_0).

## Problem

### Overview

Today, these tools are programmed to assume, within the context of app-interface data, that 'service' and 'slo-document' have a one-to-one or one-to-zero relationship (i.e. every service can have exactly 0 or 1 slo-documents).

This is consistant with most services today, but some services do in fact have multiple SLO documents

We want to properly enable the usage pattern of defining more-than-one SLO documents for any given service. We want to support 'service' and 'slo-document' having a one-to-N relationship (where N can be zero or any positive integer).

### Examples

The service 'cincinnati' [has **a single** SLO-document](https://gitlab.cee.redhat.com/service/app-interface/-/tree/1b368998a913be3f2d45a13934eb6403d4e751de/data/services/cincinnati/slo-documents). It has [three SLOs](lihttps://gitlab.cee.redhat.com/service/app-interface/-/blob/1b368998a913be3f2d45a13934eb6403d4e751de/data/services/cincinnati/slo-documents/cincinnati.yml#L13-47nk) defined. These can be seen correctly formatted in its [report YML doc](https://gitlab.cee.redhat.com/service/app-interface/-/blob/fae9d83da7db25c2ec5364eb4a6ebe8ee542e845/data/reports/Cincinnati/2021-08-01.yml#L63-78) and its [visual report page](https://visual-app-interface.devshift.net/reports#/reports/Cincinnati/2021-08-01.yml). **This is working as intended.**

The service 'ocm' [has **two** SLO-documents](https://gitlab.cee.redhat.com/service/app-interface/-/tree/1b368998a913be3f2d45a13934eb6403d4e751de/data/services/ocm/slo-documents). Each of these documents define SLOs with the same set of names (latency, errors, availability). There are a total of 6 SLOs defined for this serice (2 docs * 3 SLOs-per-doc = 6; 2 SLOs named 'latency', 2 SLOs named 'errors', and 2 SLOs named 'availability'). However, the 'ocm' [visual report page](https://visual-app-interface.devshift.net/reports#/reports/ocm/2021-08-01.yml) only renders 3 SLOs. **This is NOT working as intended.** The tools do not take into account the possibility of a service defining the same SLO name multiple times across multiple docs for the same service. Presumably the SLO datapoints in dash.db are incorrectly overwriting one another or are incorrectly being aggregated together.

The service ['service-registry'](https://gitlab.cee.redhat.com/service/app-interface/-/tree/6762ce9ae3c34abedc21abf768437a5e7753652a/data/services/service-registry/slo-documents) would have [a similar problem] (https://visual-app-interface.devshift.net/reports#/reports/service-registry/2021-08-01.yml)(although its visual report page fails to render for a seemingly-unrelated-reason) to 'ocm'.

## Proposal

### Overview

The 'name' ([example](https://gitlab.cee.redhat.com/service/app-interface/-/blob/8bba50902109207d7e8a0b8f856bec92ede1e482/data/services/ocm/slo-documents/accounts-mgmt.yml#L7)) of these SLO docs will be introduced as an identifier for the SLO metric data stored in dashdotdb.

SLO data will be stored in report-YML files in the following format:
```
service_slo:
  slo_doc_name1:
  - cluster: app-sre-prod-01
    namespace: app-interface-production
    slo_name: Reconciliation time of app-interface integrations
    slo_value: 27.0
    slo_target: 95.0
  slo_doc_name2:
  - ...
```

Visual-Qontract will have a new column `Doc Name` in the 'Service SLO' table.

### Schema Changes

Here are three proposals for how a 'slo_doc_name' identifier can be introduced to the schema:
* [Option 1] (least effort): Update the 'ServiceSLO' table to include a 'SLODocName' column of type 'string'.
* [Option 2] (author's recommendation): Update the 'ServiceSLO' table to include a 'SLODocName' column of type 'integer', which is a foreign key to a new table 'SLODocName'. Table 'SLODocName' contains 'id' (primary key, integer), and 'name' (string, unique)
    * Better data normalization that Option 1
    * Less disruptive to schema than Option 3
* [Option 3] (most effort): Same as Option 2, and in addition: update all tables that currently have a relationship with table 'ServiceSLO' to instead have a relationship with 'SLODocName'

[This PR](https://github.com/app-sre/dashdotdb/pull/50) uses the "Option 2" approach.

[This digram](https://github.com/bkez322/dashdotdb/blob/slo-doc-name-col/docs/dashdotdb.png) visualizes the proposed schema change (bottom left).


### Other Changes To DashDotDB 

* dash.db
  * this needs a "slo_doc_name" property: https://github.com/app-sre/dashdotdb/blob/master/dashdotdb/models/dashdotdb.py#L168-L179
  * update this to include "slo_doc_name": https://github.com/app-sre/dashdotdb/blob/master/examples/serviceslometrics.json
  * update this image: https://github.com/app-sre/dashdotdb/blob/master/docs/dashdotdb.png (andthe diagram file for it: https://github.com/app-sre/dashdotdb/blob/master/docs/dashdotdb.dia)
  * Follow the [DB upgrade guid](https://github.com/app-sre/dashdotdb#db-upgrade) to upgrade the schema in Postgres

### Changes To Other Systems

The following are changes to related systems that are expected to need to be made.

* app-interface
  * add "slo_doc_name": https://gitlab.cee.redhat.com/service/app-interface/-/blob/master/graphql-schemas/schema.yml#L1916-1922
  * update this to include 'slo_doc_name': https://gitlab.cee.redhat.com/service/app-interface/-/blob/master/schemas/app-sre/slo-document-1.yml
  * All of the SLO documents here need to have the new 'slo_doc_name' proeprty set: https://gitlab.cee.redhat.com/service/app-interface/-/tree/master/data/services
  * all of these same sort of changes in public-github app-interface

* visual-qontract
  * This needs to accept MULTIPLE 'slo_documents' as a parameter https://github.com/app-sre/visual-qontract/blob/bb5e993a428780ccd6a1d4208b36740e46d96f79/src/pages/elements/Report.js#L547
  * This must pass MULTIPLE 'slo_documents': https://github.com/app-sre/visual-qontract/blob/bb5e993a428780ccd6a1d4208b36740e46d96f79/src/pages/elements/Report.js#L704
  * This needs to be reethought to grab multiple slo documents, rather than just 1: https://github.com/app-sre/visual-qontract/blob/bb5e993a428780ccd6a1d4208b36740e46d96f79/src/pages/elements/Report.js#L633-L643
    * it should probably just find all slo_docs with a namespace that matches 'report.app.name' instead of just the first match

* qontract-reconcile
  * This needs to produce output matching the proposal: https://github.com/app-sre/qontract-reconcile/blob/e9612b9c6c27a961ee520461722f512b91e07926/tools/app_interface_reporter.py#L115-L121
  * This function will need significant changes toward the bottom: https://github.com/app-sre/qontract-reconcile/blob/e9612b9c6c27a961ee520461722f512b91e07926/tools/app_interface_reporter.py#L225

### Options



