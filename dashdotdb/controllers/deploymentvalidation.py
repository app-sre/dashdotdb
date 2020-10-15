from dashdotdb.services.deploymentvalidation import DeploymentValidation


def post(cluster, body):
    dv = DeploymentValidation(cluster=cluster)
    dv.insert(validation=body)
    return 'ok'


def search(cluster, namespace):
    dv = DeploymentValidation(cluster, namespace)
    return dv.get_deploymentvalidations()
