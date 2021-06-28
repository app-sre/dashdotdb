from flask import Response

from prometheus_client import Counter
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest

from dashdotdb.services.imagemanifestvuln import ImageManifestVuln


def search():
    imv = ImageManifestVuln()
    imv_results = imv.get_vulnerabilities_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    imv_counter = Counter('imagemanifestvuln',
                          labelnames=('cluster', 'namespace', 'severity'),
                          documentation='Vulnerabilities total per severity',
                          registry=registry)

    for result in imv_results:
        imv_counter.labels(cluster=result.Cluster.name,
                           namespace=result.Namespace.name,
                           severity=result.Severity.name).inc(result.Count)

    headers = {'Content-type': 'text/plain'}
    return Response(generate_latest(registry=registry), 200, headers)
