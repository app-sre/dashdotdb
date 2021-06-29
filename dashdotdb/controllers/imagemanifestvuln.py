from dashdotdb.services.imagemanifestvuln import ImageManifestVuln
from dashdotdb.controllers.transactions import add_to_transaction


def post(transactionid, cluster, body):
    imv = ImageManifestVuln(cluster=cluster, manifest=body)
    add_to_transaction(transactionid, imv)
    return 'ok'


def search(cluster, namespace):
    imv = ImageManifestVuln(cluster=cluster, namespace=namespace)
    return imv.get_vulnerabilities()
