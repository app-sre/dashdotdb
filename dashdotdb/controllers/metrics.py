from flask import Response

from prometheus_client import Counter
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest

from dashdotdb.services.imagemanifestvuln import ImageManifestVuln
from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def search():
    imv = ImageManifestVuln()
    imv_results = imv.get_vulnerabilities_summary()

    dpv = DeploymentValidationData()
    dpv_results = dpv.get_deploymentvalidation_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    counter = Counter('imagemanifestvuln',
                      labelnames=('cluster', 'namespace', 'severity'),
                      documentation='Vulnerabilities total per severity',
                      registry=registry)

    counter = Counter('deploymentvalidation',
                      labelnames=('cluster', 'namespace', 'validation',
                                  'status'),
                      documentation='Validation success by validation type',
                      registry=registry)

    for result in imv_results:
        counter.labels(cluster=result.Cluster.name,
                       namespace=result.Namespace.name,
                       severity=result.Severity.name).inc(result.Count)
    for result in dpv_results:
        counter.labels(cluster=result.DVCluster.name,
                       namespace=result.DVNamespace.name,
                       validation=result.validation.name,
                       status=result.validation.status).inc(result.Count)

    headers = {'Content-type': 'text/plain'}
    return Response(generate_latest(registry=registry), 200, headers)
