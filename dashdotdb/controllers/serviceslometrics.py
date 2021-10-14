from dashdotdb.services.serviceslometrics import ServiceSLOMetrics
from dashdotdb.services.serviceslometrics import ServiceSLOMetricsInput


def post(user, name, body):
    slo = ServiceSLOMetrics(name=name)
    slo.insert(token=user, slo=body)
    return 'ok'


def search(cluster, namespace, sli_type, slo_doc, name):
    input = ServiceSLOMetricsInput()
    input.cluster = cluster
    input.namespace = namespace
    input.sli_type = sli_type
    input.slo_doc = slo_doc
    input.name = name

    slo = ServiceSLOMetrics(input)
    return slo.get_slometrics()
