import logging

from datetime import datetime
from datetime import timedelta

from sqlalchemy import func

from dashdotdb.models.deploymentvalidation import db
from dashdotdb.models.deploymentvalidation import Token
from dashdotdb.models.deploymentvalidation import Cluster
from dashdotdb.models.deploymentvalidation import Namespace
from dashdotdb.models.deploymentvalidation import DeploymentValidation
from dashdotdb.models.deploymentvalidation import Validation
from dashdotdb.models.deploymentvalidation import ObjectKind


class DeploymentValidation:
    def __init__(self, cluster=None, namespace=None):
        self.log = logging.getLogger()

        self.cluster = cluster
        self.namespace = namespace

    def insert(self, validation):
        for item in validation['items']:
            self._insert(item)

    def _insert(self, item):
        if 'kind' not in item:
            self.log.error('skipping validation: key "kind" not found')
            return

        if item['kind'] != 'DeploymentValidation':
            self.log.info('skipping kind "%s"', item["kind"])
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

        namespace_name = item['metadata']['namespace']
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()
        if db_namespace is None:
            db.session.add(Namespace(name=namespace_name,
                                     cluster_id=db_cluster.id))
            db.session.commit()
            self.log.info('namespace %s created', namespace_name)
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()

        image_name = item['spec']['image']
        image_validation = item['spec']['validation']
        db_image = db.session.query(Image) \
            .filter_by(name=image_name, validation=image_validation).first()
        if db_image is None:
            db.session.add(Image(name=image_name,
                                 validation=image_validation))
            db.session.commit()
            self.log.info('image %s created', image_name)
        db_image = db.session.query(Image) \
            .filter_by(name=image_name, validation=image_validation).first()

        features = item['spec']['features']
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

    def get_validations(self):
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
                for validation in feature.validations:
                    result.append(
                        {
                            'repository': image.name,
                            'name': feature.namespacename,
                            'validation': image.validation[:14],
                            'affected_pods': len(image.pods),
                            'validation': validation.name,
                            'link': validation.link,
                        }
                    )

        return result

    @staticmethod
    def get_deploymentvalidation_summary():
        """
        select cluster.name, max(token.id)
        from token, deploymentvalidation, namespace, cluster
        where token.id = deploymentvalidation.token_id
        and deploymentvalidation.namespace_id = namespace.id
        and namespace.cluster_id = cluster.id
        group by cluster.name
        """

        token = db.session.query(
            db.func.max(Token.id).label('token_id')
        ).filter(
            Token.id == DeploymentValidation.token_id,
            DeploymentValidation.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id
        )

        results = db.session.query(
            Cluster,
            Namespace,
            DeploymentValidation,
            func.count(Validation.name).label('Count')
        ).filter(
            Validation.severity_id == Severity.id,
            Validation.feature_id == Feature.id,
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
