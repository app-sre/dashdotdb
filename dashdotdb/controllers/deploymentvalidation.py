from dashdotdb.services.deploymentvalidation import DeploymentValidationData


def post(cluster, body):
    dv = DeploymentValidationData(cluster=cluster)
    dv.insert(validation=body)
    return 'ok'


def search(cluster, namespace):
    dv = DeploymentValidationData(cluster, namespace)
    return dv.get_deploymentvalidations()
