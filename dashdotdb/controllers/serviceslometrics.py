from dashdotdb.services.serviceslometrics import ServiceSLOMetrics
from dashdotdb.services.serviceslometrics import ServiceSLOMetricsInput


def post(user, name: str, body):
    input_props = ServiceSLOMetricsInput()
    input_props.name = name
    slo = ServiceSLOMetrics(input_props=input_props)
    slo.insert(token=user, slo=body)
    return 'ok'


def search(cluster: str, namespace: str,
           sli_type: str, slo_doc: str, name: str):
    input_props = ServiceSLOMetricsInput()
    input_props.cluster = cluster
    input_props.namespace = namespace
    input_props.sli_type = sli_type
    input_props.slo_doc = slo_doc
    input_props.name = name

    slo = ServiceSLOMetrics(input_props=input_props)
    return slo.get_slometrics()
