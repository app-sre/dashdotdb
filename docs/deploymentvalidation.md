# deploment validation 
XXWIPXX

## Example Source Data
Current dv validation/metrics:
* replicas
* requests_limites

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

## Example Target Metrics

```
# deployment_validation_total{}
deployment_validation_total{cluster="app-sre-prod-01",namespace="fooblah",validation="replicas"} 10.0
deployment_validation_total{cluster="app-sre-prod-01",namespace="fooblah",validation="requests_limits"} 0.0
...
```
 
