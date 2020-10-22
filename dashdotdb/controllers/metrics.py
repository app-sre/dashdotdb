from flask import Response

from prometheus_client import Counter
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest

from dashdotdb.services.imagemanifestvuln import ImageManifestVuln
from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def search():
    imv = ImageManifestVuln()
    results = imv.get_vulnerabilities_summary()

    dpv = DeploymentValidationData()
    results = dpv.get_deploymentvalidation_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    counter = Counter('imagemanifestvuln',
                      labelnames=('cluster', 'namespace', 'severity'),
                      documentation='Vulnerabilities total per severity',
                      registry=registry)

#    counter = Counter('deploymentvalidation',
#                      labelnames=('cluster', 'namespace', 'validation'),
#                      documentation='Validations total per status',
#                      registry=registry)

    for result in results:
        counter.labels(cluster=result.Cluster.name,
                       namespace=result.Namespace.name,
                       severity=result.Severity.name).inc(result.Count)
#        counter.labels(cluster=result.Cluster.name,
#                       namespace=result.Namespace.name,
#                       validation=result.validation.name).inc(result.Count)

    headers = {'Content-type': 'text/plain'}
    return Response(generate_latest(registry=registry), 200, headers)
