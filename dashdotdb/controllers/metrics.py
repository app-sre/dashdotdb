from flask import Response

from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest

from dashdotdb.services.imagemanifestvuln import ImageManifestVuln
from dashdotdb.services.deploymentvalidation import DeploymentValidationData
from dashdotdb.services.serviceslometrics import ServiceSLOMetrics


def search():
    imv = ImageManifestVuln()
    imv_results = imv.get_vulnerabilities_summary()

    dpv = DeploymentValidationData()
    dpv_results = dpv.get_deploymentvalidation_summary()

    slo = ServiceSLOMetrics()
    slo_results = slo.get_slometrics_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    imv_counter = Counter('imagemanifestvuln',
                          labelnames=('cluster', 'namespace', 'severity'),
                          documentation='Vulnerabilities total per severity',
                          registry=registry)

    dv_counter = Counter('deploymentvalidation',
                         labelnames=('cluster', 'namespace', 'validation',
                                     'status'),
                         documentation='Validations by validation type',
                         registry=registry)

    slo_gauge = Gauge('serviceslometrics',
                      labelnames=('cluster', 'namespace', 'service',
                                  'slitype', 'name', 'type'),
                      documentation=("ServiceSLOMetrics by cluster,"
                                     "service, namespace, slitype,"
                                     "name, type"),
                      registry=registry)

    for result in imv_results:
        imv_counter.labels(cluster=result.Cluster.name,
                           namespace=result.Namespace.name,
                           severity=result.Severity.name).inc(result.Count)

    for result in dpv_results:
        dv_counter.labels(cluster=result.Cluster.name,
                          namespace=result.Namespace.name,
                          validation=result.Validation.name,
                          status=result.Validation.status).inc(result.Count)

    for result in slo_results:
        slo_gauge.labels(cluster=result.Cluster.name,
                         namespace=result.Namespace.name,
                         service=result.Service.name,
                         slitype=result.SLIType.name,
                         name=result.ServiceSLO.name,
                         type='slo_value').set(result.ServiceSLO.value)
        slo_gauge.labels(cluster=result.Cluster.name,
                         namespace=result.Namespace.name,
                         service=result.Service.name,
                         slitype=result.SLIType.name,
                         name=result.ServiceSLO.name,
                         type='slo_target').set(result.ServiceSLO.target)

    headers = {'Content-type': 'text/plain'}
    return Response(generate_latest(registry=registry), 200, headers)
