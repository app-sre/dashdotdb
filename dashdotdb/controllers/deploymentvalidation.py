from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def post(cluster, body):
    dpv = DeploymentValidationData(cluster=cluster)
    dpv.insert(validation=body)
    return 'ok'


def search(cluster, namespace):
    dpv = DeploymentValidationData(cluster, namespace)
    return dpv.get_deploymentvalidations()
