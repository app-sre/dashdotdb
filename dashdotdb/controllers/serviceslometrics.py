from dashdotdb.services.serviceslometrics import ServiceSLOMetrics


def post(user, name, body):
    slo = ServiceSLOMetrics(name=name)
    slo.insert(token=user, slo=body)
    return 'ok'


def search(cluster, namespace, sli_type, slo_doc, name):
    slo = ServiceSLOMetrics(cluster, namespace, sli_type, slo_doc, name)
    return slo.get_slometrics()
