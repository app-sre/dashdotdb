from dashdotdb.services.deploymentvalidation import DeploymentValidationData
from dashdotdb.controllers.tokens import generate_token, close_token


def post(token, cluster, body):
    dpv = DeploymentValidationData(cluster=cluster)
    dpv.insert(token=token, validation=body)
    return 'ok'


def search(cluster, namespace):
    dpv = DeploymentValidationData(cluster=cluster, namespace=namespace)
    return dpv.get_deploymentvalidations()


def newtoken():
    return generate_token("DVOType")


def closetoken(token):
    return close_token(token, "DVOType")
