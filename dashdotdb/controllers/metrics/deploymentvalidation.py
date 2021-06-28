from flask import Response

from prometheus_client import Counter
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest

from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def search():
    dpv = DeploymentValidationData()
    dpv_results = dpv.get_deploymentvalidation_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    dv_counter = Counter('deploymentvalidation',
                         labelnames=('cluster', 'namespace', 'validation',
                                     'status'),
                         documentation='Validations by validation type',
                         registry=registry)

    for result in dpv_results:
        dv_counter.labels(cluster=result.Cluster.name,
                          namespace=result.Namespace.name,
                          validation=result.Validation.name,
                          status=result.Validation.status).inc(result.Count)

    headers = {'Content-type': 'text/plain'}
    return Response(generate_latest(registry=registry), 200, headers)
