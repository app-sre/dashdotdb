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


class DeploymentValidationData:
    def __init__(self, cluster=None, namespace=None):
        self.log = logging.getLogger()

        self.cluster = cluster
        self.namespace = namespace

    def insert(self, validation):
        for item in validation['items']:
            self._insert(item)

    def _insert(self, item):
        if 'metric' not in item:
            self.log.error('skipping validation: key "metric" not found')
            return

        if item['metric'] != 'DeploymentValidation':
            self.log.info('skipping metric "%s"', item["metric"])
            return

        expire = datetime.now() - timedelta(minutes=60)
        db_validationtoken = db.session.query(ValidationToken) \
            .filter(ValidationToken.timestamp > expire).first()
        if db_validationtoken is None:
            db.session.add(ValidationToken(timestamp=datetime.now()))
            db.session.commit()
            self.log.info('validationtoken created')
        db_validationtoken = db.session.query(ValidationToken) \
            .filter(ValidationToken.timestamp > expire).first()

        cluster_name = self.cluster
        db_cluster = db.session.query(DVCluster) \
            .filter_by(name=cluster_name).first()
        if db_cluster is None:
            db.session.add(DVCluster(name=cluster_name))
            db.session.commit()
            self.log.info('cluster %s created', cluster_name)
        db_cluster = db.session.query(DVCluster) \
            .filter_by(name=cluster_name).first()

        namespace_name = item['metadata']['namespace']
        db_namespace = db.session.query(DVNamespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()
        if db_namespace is None:
            db.session.add(DVNamespace(name=namespace_name,
                                       cluster_id=db_cluster.id))
            db.session.commit()
            self.log.info('namespace %s created', namespace_name)
        db_namespace = db.session.query(DVNamespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()

        validation_name = item['metric']['__name__']
        validation_status = item['value'][1]
#       validation_namespace = item['metric']['exported_namespace']
        db_validation = db.session.query(Validation) \
            .filter_by(name=validation_name, status=validation_status).first()
        if db_validation is None:
            db.session.add(Validation(name=validation_name,
                                      status=validation_status))
            db.session.commit()
            self.log.info('validation %s:%s created', validation_name,
                          validation_status)
        db_validation = db.session.query(Validation) \
            .filter_by(name=validation_name, status=validation_status).first()

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

    def get_deploymentvalidations(self):
        validationtoken = db.session.query(ValidationToken) \
            .filter(DeploymentValidation.token_id == ValidationToken.id,
                    DeploymentValidation.namespace_id == DVNamespace.id,
                    DVNamespace.cluster_id == DVCluster.id,
                    DVCluster.name == self.cluster) \
            .order_by(ValidationToken.timestamp.desc()) \
            .limit(1) \
            .first()
        if validationtoken is None:
            return []

        validations = db.session.query(Validation) \
            .filter(Validation.id == DeploymentValidation.validation_id,
                    DeploymentValidation.tokenz == validationtoken.id,
                    DeploymentValidation.namespace_id == DVNamespace.id,
                    DeploymentValidation.objectkind_id == ObjectKind.id,
                    DVNamespace.name == self.namespace,
                    DVNamespace.cluster_id == DVCluster.id,
                    DVCluster.name == self.cluster).all()

        result = list()
        for validation in validations:
            result.append({'name': validation.name,
                           'status': validation.status
                           })
        return result

    @staticmethod
    def get_deploymentvalidation_summary():
        """
        select cluster.name, max(validationtoken.id)
        from validationtoken, deploymentvalidation, dvnamespace, dvcluster,
        where validationtoken.id = deploymentvalidation.token_id
        and deploymentvalidation.namespace_id = dvnamespace.id
        and dvnamespace.cluster_id = dvcluster.id
        group by dvcluster.name
        """

        validationtoken = db.session.query(
            db.func.max(ValidationToken.id).label('validationtoken_id')
        ).filter(
            ValidationToken.id == DeploymentValidation.token_id,
            DeploymentValidation.namespace_id == DVNamespace.id,
            DVNamespace.cluster_id == DVCluster.id
        )

        results = db.session.query(
            DVCluster,
            DVNamespace,
            DeploymentValidation,
            func.count(Validation.name).label('Count')
        ).filter(
            DeploymentValidation.validation_id == Validation.id,
            DeploymentValidation.token_id == ValidationToken.id,
            DeploymentValidation.namespace_id == DVNamespace.id,
            DVNamespace.cluster_id == DVCluster.id,
            ValidationToken.id == validationtoken[0].Yalidationtoken_id
        ).group_by(
            Validation, DVNamespace, DVCluster
        )

        return results
