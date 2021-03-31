from dashdotdb.services.serviceslometrics import ServiceSLOMetrics


def post(name, body):
    slo = ServiceSLOMetrics(name=name)
    slo.insert(slo=body)
    return 'ok'


def search(cluster, namespace, sli_type, name):
    slo = ServiceSLOMetrics(cluster, namespace, sli_type, name)
    return slo.get_slometrics()
