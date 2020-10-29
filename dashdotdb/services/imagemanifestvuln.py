import logging

from datetime import datetime
from datetime import timedelta

from sqlalchemy import func

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Token
from dashdotdb.models.dashdotdb import Cluster
from dashdotdb.models.dashdotdb import Namespace
from dashdotdb.models.dashdotdb import Pod
from dashdotdb.models.dashdotdb import Image
from dashdotdb.models.dashdotdb import ImageFeature
from dashdotdb.models.dashdotdb import Feature
from dashdotdb.models.dashdotdb import Vulnerability
from dashdotdb.models.dashdotdb import Severity


class ImageManifestVuln:
    def __init__(self, cluster=None, namespace=None):
        self.log = logging.getLogger()

        self.cluster = cluster
        self.namespace = namespace

    def insert(self, manifest):
        if 'kind' not in manifest:
            self.log.error('skipping manifest: key "kind" not found')
            return

        if manifest['kind'] != 'ImageManifestVuln':
            self.log.info('skipping kind "%s"', manifest["kind"])
            return

        expire = datetime.now() - timedelta(minutes=60)
        db_token = db.session.query(Token) \
            .filter(Token.timestamp > expire).first()
        if db_token is None:
            db.session.add(Token(timestamp=datetime.now()))
            db.session.commit()
            self.log.info('token created')
        db_token = db.session.query(Token) \
            .filter(Token.timestamp > expire).first()

        cluster_name = self.cluster
        db_cluster = db.session.query(Cluster) \
            .filter_by(name=cluster_name).first()
        if db_cluster is None:
            db.session.add(Cluster(name=cluster_name))
            db.session.commit()
            self.log.info('cluster %s created', cluster_name)
        db_cluster = db.session.query(Cluster) \
            .filter_by(name=cluster_name).first()

        namespace_name = manifest['metadata']['namespace']
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()
        if db_namespace is None:
            db.session.add(Namespace(name=namespace_name,
                                     cluster_id=db_cluster.id))
            db.session.commit()
            self.log.info('namespace %s created', namespace_name)
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()

        image_name = manifest['spec']['image']
        image_manifest = manifest['spec']['manifest']
        db_image = db.session.query(Image) \
            .filter_by(name=image_name, manifest=image_manifest).first()
        if db_image is None:
            db.session.add(Image(name=image_name,
                                 manifest=image_manifest))
            db.session.commit()
            self.log.info('image %s created', image_name)
        db_image = db.session.query(Image) \
            .filter_by(name=image_name, manifest=image_manifest).first()

        features = manifest['spec']['features']
        for feature in features:
            feature_name = feature['name']
            feature_namespacename = feature['namespaceName']
            feature_version = feature['version']
            feature_versionformat = feature['versionformat']
            db_feature = db.session.query(Feature) \
                .filter_by(name=feature_name,
                           namespacename=feature_namespacename,
                           version=feature_version,
                           versionformat=feature_versionformat) \
                .filter(Feature.images.any(id=db_image.id)).first()
            if db_feature is None:
                db.session.add(Feature(name=feature_name,
                                       namespacename=feature_namespacename,
                                       version=feature_version,
                                       versionformat=feature_versionformat,
                                       images=[db_image]))
                db.session.commit()
                self.log.info('feature %s created ', feature_name)

            db_feature = db.session.query(Feature) \
                .filter_by(name=feature_name,
                           namespacename=feature_namespacename,
                           version=feature_version,
                           versionformat=feature_versionformat) \
                .filter(Feature.images.any(id=db_image.id)).first()

            vulnerabilities = feature['vulnerabilities']
            for vulnerability in vulnerabilities:
                vulnerability_name = vulnerability['name']
                vulnerability_descr = vulnerability.get('description')
                vulnerability_link = vulnerability.get('link')
                vulnerability_fixedby = vulnerability.get('fixedby')
                vulnerability_severity = vulnerability['severity']
                db_severity = db.session.query(Severity) \
                    .filter_by(name=vulnerability_severity).first()
                if db_severity is None:
                    db.session.add(Severity(name=vulnerability_severity))
                    db.session.commit()
                    self.log.info('severity %s created ',
                                  vulnerability_severity)
                db_severity = db.session.query(Severity) \
                    .filter_by(name=vulnerability_severity).first()

                db_vulnerability = db.session.query(Vulnerability) \
                    .filter_by(name=vulnerability_name,
                               description=vulnerability_descr,
                               fixedby=vulnerability_fixedby,
                               link=vulnerability_link,
                               severity_id=db_severity.id,
                               feature_id=db_feature.id).first()
                if db_vulnerability is None:
                    db.session.add(Vulnerability(
                        name=vulnerability_name,
                        description=vulnerability_descr,
                        fixedby=vulnerability_fixedby,
                        link=vulnerability_link,
                        severity_id=db_severity.id,
                        feature_id=db_feature.id
                    ))
                    db.session.commit()
                    self.log.info('vulnerability %s created ',
                                  vulnerability_name)

        pods = manifest['status']['affectedPods'].keys()
        for pod in pods:
            db_pod = db.session.query(Pod) \
                .filter_by(name=pod,
                           namespace_id=db_namespace.id,
                           image_id=db_image.id,
                           token_id=db_token.id).first()
            if db_pod is None:
                db.session.add(Pod(name=pod,
                                   namespace_id=db_namespace.id,
                                   image_id=db_image.id,
                                   token_id=db_token.id))
                db.session.commit()
                self.log.info('pod %s created', pod)

    def get_vulnerabilities(self):
        token = db.session.query(Token) \
            .filter(Pod.token_id == Token.id,
                    Pod.namespace_id == Namespace.id,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster) \
            .order_by(Token.timestamp.desc()) \
            .limit(1) \
            .first()
        if token is None:
            return []

        images = db.session.query(Image) \
            .filter(Image.id == Pod.image_id,
                    Pod.token_id == token.id,
                    Pod.namespace_id == Namespace.id,
                    Namespace.name == self.namespace,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster).all()

        result = list()
        for image in images:
            for feature in image.features:
                for vulnerability in feature.vulnerabilities:
                    result.append(
                        {
                            'repository': image.name,
                            'name': feature.namespacename,
                            'manifest': image.manifest[:14],
                            'affected_pods': len(image.pods),
                            'vulnerability': vulnerability.name,
                            'severity': vulnerability.severity.name,
                            'package': feature.name,
                            'current_version': feature.version,
                            'fixed_in_version': vulnerability.fixedby,
                            'link': vulnerability.link,
                        }
                    )

        return result

    @staticmethod
    def get_vulnerabilities_summary():
        """
        select cluster.name, max(token.id)
        from token, pod, namespace, cluster
        where token.id = pod.token_id
        and pod.namespace_id = namespace.id
        and namespace.cluster_id = cluster.id
        group by cluster.name
        """

        token = db.session.query(
            db.func.max(Token.id).label('token_id')
        ).filter(
            Token.id == Pod.token_id,
            Pod.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id
        )

        results = db.session.query(
            Cluster,
            Namespace,
            Severity,
            func.count(Vulnerability.name).label('Count')
        ).filter(
            Vulnerability.severity_id == Severity.id,
            Vulnerability.feature_id == Feature.id,
            Feature.id == ImageFeature.feature_id,
            ImageFeature.image_id == Image.id,
            Image.id == Pod.image_id,
            Pod.token_id == Token.id,
            Pod.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id,
            Token.id == token[0].token_id
        ).group_by(
            Severity, Namespace, Cluster
        )

        return results
