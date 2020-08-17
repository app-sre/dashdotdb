from dashdotdb.services.imagemanifestvuln import ImageManifestVuln


def post(cluster, body):
    imv = ImageManifestVuln(cluster=cluster)
    imv.insert(manifest=body)
    return 'ok'


def search(cluster, namespace):
    imv = ImageManifestVuln(cluster, namespace)
    return imv.get_vulnerabilities()
