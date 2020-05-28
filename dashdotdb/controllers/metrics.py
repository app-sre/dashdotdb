from flask import Response

from prometheus_client import Counter
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest


from dashdotdb.services.imagemanifestvuln import ImageManifestVuln


def search():

    imv = ImageManifestVuln()
    results = imv.get_vulnerabilities_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    counter = Counter('imagemanifestvuln',
                      labelnames=('cluster', 'namespace', 'severity'),
                      documentation='Vulnerabilities total per severity',
                      registry=registry)

    for result in results:
        counter.labels(cluster=result.Cluster.name,
                       namespace=result.Namespace.name,
                       severity=result.Severity.name).inc()

    headers = {'Content-type': 'text/plain'}
    return Response(generate_latest(registry=registry), 200, headers)
