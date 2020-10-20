import logging

from datetime import datetime
from datetime import timedelta

from sqlalchemy import func

from dashdotdb.models.deploymentvalidation import db
from dashdotdb.models.deploymentvalidation import ValidationToken
from dashdotdb.models.deploymentvalidation import DVCluster
from dashdotdb.models.deploymentvalidation import DVNamespace
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
        db_validationtoken = db.session.query(Token) \
            .filter(Token.timestamp > expire).first()
        if db_validationtoken is None:
            db.session.add(Token(timestamp=datetime.now()))
            db.session.commit()
            self.log.info('validationtoken created')
        db_validationtoken = db.session.query(Token) \
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

        objectkind = item['metric']['kind']
        db_objectkind = db.session.query(ObjectKind) \
            .filter_by(name=objectkind).first()
        if db_objectkind is None:
            db.session.add(ObjectKind(name=objectkind))
            db.session.commit()
            self.log.info('objectkind %s created ', objectkind)

        db_objectkind = db.session.query(ObjectKind) \
            .filter_by(name=objectkind) \
            .filter(ObjectKind.name.any(id=db_objectkind.id)).first()

    def get_validations(self):
        validationtoken = db.session.query(Token) \
            .filter(Pod.validationtoken_id == Token.id,
                    Pod.namespace_id == Namespace.id,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster) \
            .order_by(Token.timestamp.desc()) \
            .limit(1) \
            .first()
        if validationtoken is None:
            return []

        images = db.session.query(Image) \
            .filter(Image.id == Pod.image_id,
                    Pod.validationtoken_id == validationtoken.id,
                    Pod.namespace_id == Namespace.id,
                    Namespace.name == self.namespace,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster).all()

        result = list()
        for image in images:
            for kind in image.kinds:
                for validation in kind.validations:
                    result.append(
                        {
                            'repository': image.name,
                            'name': kind.namespacename,
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
        select cluster.name, max(validationtoken.id)
        from validationtoken, deploymentvalidation, namespace, cluster
        where validationtoken.id = deploymentvalidation.validationtoken_id
        and deploymentvalidation.namespace_id = namespace.id
        and namespace.cluster_id = cluster.id
        group by cluster.name
        """

        validationtoken = db.session.query(
            db.func.max(Token.id).label('validationtoken_id')
        ).filter(
            Token.id == DeploymentValidation.validationtoken_id,
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
            Pod.validationtoken_id == Token.id,
            Pod.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id,
            Token.id == validationtoken[0].validationtoken_id
        ).group_by(
            Severity, Namespace, Cluster
        )

        return results
