from dashdotdb.services.serviceslometrics import ServiceSLOMetrics
from dashdotdb.controllers.transactions import add_to_transaction


def post(transactionid, name, body):
    slo = ServiceSLOMetrics(name=name, slo=body)
    add_to_transaction(transactionid, slo)
    return 'ok'


def search(cluster, namespace, sli_type, name):
    slo = ServiceSLOMetrics(
        cluster=cluster, namespace=namespace, sli_type=sli_type, name=name)
    return slo.get_slometrics()
