from dashdotdb.services.serviceslometrics import ServiceSLOMetrics


def post(cluster, body):
    imv = ServiceSLOMetrics(cluster=cluster)
    imv.insert(slo=body)
    return 'ok'

def search(cluster, namespace, sli_type, name):
    imv = ServiceSLOMetrics(cluster, namespace, sli_type, name)
    return imv.get_slometrics()

