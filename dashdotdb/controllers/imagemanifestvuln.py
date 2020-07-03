from flask import current_app
from flask import jsonify
from flask import request

from dashdotdb.services.imagemanifestvuln import ImageManifestVuln


def post(cluster, body):
    authorization = request.headers.get('Authorization')
    if authorization != f'token: {current_app.config["ACCESS_TOKEN"]}':
        return jsonify(message='Access denied'), 401

    imv = ImageManifestVuln(cluster=cluster)
    imv.insert(manifest=body)
    return 'ok'


def search(cluster, namespace):
    authorization = request.headers.get('Authorization')
    if authorization != f'token: {current_app.config["ACCESS_TOKEN"]}':
        return jsonify(message='Access denied'), 401

    imv = ImageManifestVuln(cluster, namespace)
    return imv.get_vulnerabilities()
