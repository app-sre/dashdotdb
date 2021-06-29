from dashdotdb.services.deploymentvalidation import DeploymentValidationData
from dashdotdb.controllers.transactions import add_to_transaction


def post(transactionid, cluster, body):
    dpv = DeploymentValidationData(cluster=cluster, validation=body)
    add_to_transaction(transactionid, dpv)
    return 'ok'


def search(cluster, namespace):
    dpv = DeploymentValidationData(cluster=cluster, namespace=namespace)
    return dpv.get_deploymentvalidations()
