from flask import Response

from prometheus_client import Gauge
from prometheus_client import CollectorRegistry
from prometheus_client import ProcessCollector
from prometheus_client import generate_latest

from dashdotdb.services.serviceslometrics import ServiceSLOMetrics


def search():
    slo = ServiceSLOMetrics()
    slo_results = slo.get_slometrics_summary()

    registry = CollectorRegistry()
    ProcessCollector(registry=registry)

    slo_gauge = Gauge('serviceslometrics',
                      labelnames=('cluster', 'namespace', 'service',
                                  'slitype', 'name', 'type'),
                      documentation=("ServiceSLOMetrics by cluster,"
                                     "service, namespace, slitype,"
                                     "name, type"),
                      registry=registry)

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
