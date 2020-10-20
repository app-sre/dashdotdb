# deploment validation 
XXWIPXX


## Example Data Blobs
Current dv validation/metrics:
* replicas
* requests_limites

### Prometheus (Raw)
Ex: https://prometheus.fqdn/api/v1/query?query=deployment_validation_operator_replica_validation&_=1603207652262
```
# deployment_validation_operator_replica_validation{}
deployment_validation_operator_replica_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="Deployment",name="qontract-reconcile-terraform-vpc-peerings",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"}  1
deployment_validation_operator_replica_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="Deployment",name="qontract-reconcile-unleash-watcher",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"} 1
deployment_validation_operator_replica_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="ReplicaSet",name="openshift-acme-d6bdb5b48",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"} 1
deployment_validation_operator_replica_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="ReplicaSet",name="qontract-api-58867cb74d",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"} 0

# deployment_validation_operator_request_limit_validation{}
deployment_validation_operator_request_limit_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="Deployment",name="qontract-reconcile-terraform-vpc-peerings",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"}  0
deployment_validation_operator_request_limit_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="Deployment",name="qontract-reconcile-unleash-watcher",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"} 0
deployment_validation_operator_request_limit_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="ReplicaSet",name="openshift-acme-d6bdb5b48",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"} 1
deployment_validation_operator_request_limit_validation{endpoint="http-metrics",exported_namespace="app-interface-stage",instance="10.129.2.12:8383",job="deployment-validation-operator-metrics",kind="ReplicaSet",name="qontract-api-58867cb74d",namespace="app-sre",pod="deployment-validation-operator-7765765885-5rlbp",service="deployment-validation-operator-metrics"} 0
```
#### Prometheus (JSON))
```
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "__name__": "deployment_validation_operator_replica_validation",
          "endpoint": "http-metrics",
          "exported_namespace": "visual-qontract-stage",
          "instance": "10.130.3.29:8383",
          "job": "deployment-validation-operator-metrics",
          "kind": "ReplicaSet",
          "name": "openshift-acme-d6bdb5b48",
          "namespace": "deployment-validation-operator",
          "pod": "deployment-validation-operator-6bb5b5cfd-27mwd",
          "service": "deployment-validation-operator-metrics"
        },
        "value": [
          1603208289.29,
          "1"
        ]
      }
    ]
  }
}
```

## Endpoint Input (JSON)
```
{
  "items": [
    {
      "metric": {
        "__name__": "deployment_validation_operator_replica_validation",
        "exported_namespace": "visual-qontract-stage",
        "kind": "ReplicaSet",
        "name": "openshift-acme-d6bdb5b48"
      },
      "value": [
        1603208289.29,
        "1"
      ]
    }
  ]
}
```

## Endpoint Output (Raw)

```
# deployment_validation_total{}
deployment_validation_total{cluster="app-sre-prod-01",namespace="fooblah",validation="replicas",status="1"} 10.0
deployment_validation_total{cluster="app-sre-prod-01",namespace="fooblah",validation="requests_limits",status="1"} 0.0
...
```
 
## Endpoint Output (JSON)
Count by cluster | namespace | validation | status
```
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "__name__": "deployment_validation_total",
          "cluster": "app-sre-prod-01",
          "namespace": "visual-qontract-stage",
          "kind": "ReplicaSet",
          "name": "openshift-acme-d6bdb5b48",
          "validation": "replicas",
          "status": "1"
        },
        "value": [
          1603208289.29,
          "10"
        ]
      }
    ]
  }
```
