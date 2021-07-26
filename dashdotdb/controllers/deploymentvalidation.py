from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def post(user, cluster, body):
    dpv = DeploymentValidationData(cluster=cluster)
    return dpv.insert(token=user, validation=body)


def search(cluster, namespace):
    dpv = DeploymentValidationData(cluster=cluster, namespace=namespace)
    return dpv.get_deploymentvalidations()
