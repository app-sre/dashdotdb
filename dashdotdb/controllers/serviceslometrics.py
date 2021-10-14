from dashdotdb.services.serviceslometrics import ServiceSLOMetrics
from dashdotdb.services.serviceslometrics import ServiceSLOMetricsInput


def post(user, name, body):
    slo = ServiceSLOMetrics(name=name)
    slo.insert(token=user, slo=body)
    return 'ok'


def search(cluster, namespace, sli_type, slo_doc, name):
    inputProperties = ServiceSLOMetricsInput()
    inputProperties.cluster = cluster
    inputProperties.namespace = namespace
    inputProperties.sli_type = sli_type
    inputProperties.slo_doc = slo_doc
    inputProperties.name = name

    slo = ServiceSLOMetrics(inputProperties=inputProperties)
    return slo.get_slometrics()
