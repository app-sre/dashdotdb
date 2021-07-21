from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def post(token, cluster, body):
    dpv = DeploymentValidationData(cluster=cluster)
    return dpv.insert(token=token, validation=body)


def search(cluster, namespace):
    dpv = DeploymentValidationData(cluster=cluster, namespace=namespace)
    return dpv.get_deploymentvalidations()
