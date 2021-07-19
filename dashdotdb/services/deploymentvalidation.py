import logging

from datetime import datetime
from datetime import timedelta

from sqlalchemy import func

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Tokens
from dashdotdb.models.dashdotdb import LatestTokens
from dashdotdb.models.dashdotdb import Cluster
from dashdotdb.models.dashdotdb import Namespace
from dashdotdb.models.dashdotdb import DeploymentValidation
from dashdotdb.models.dashdotdb import Validation
from dashdotdb.models.dashdotdb import ObjectKind
from dashdotdb.services import DataTypes


class DeploymentValidationData:
    def __init__(self, cluster=None, namespace=None):
        self.log = logging.getLogger()

        self.cluster = cluster
        self.namespace = namespace

    def insert(self, token, validation=None):
        if validation:
            for item in validation['data']['result']:
                self._insert(token, item)

    def _insert(self, token, item):
        if 'metric' not in item:
            self.log.error('skipping validation: key "metric" not found')
            return

        if 'value' not in item:
            self.log.error('skipping validation: key "value" not found')
            return

        db_token = db.session.query(Tokens) \
            .filter(Tokens.uuid == token,
                    Tokens.data_type == DataTypes.DVODataType).first()
        if db_token is None:
            self.log.error(f'skipping validation: token not found: {token}')
            return

        if not db_token.is_open:
            self.log.error(
                f'skipping validation: token {token} is closed for data')
            return

        cluster_name = self.cluster
        db_cluster = db.session.query(Cluster) \
            .filter_by(name=cluster_name).first()
        if db_cluster is None:
            db.session.add(Cluster(name=cluster_name))
            db.session.commit()
            self.log.info('cluster %s created', cluster_name)
        db_cluster = db.session.query(Cluster) \
            .filter_by(name=cluster_name).first()

        namespace_name = item['metric']['exported_namespace']
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()
        if db_namespace is None:
            db.session.add(Namespace(name=namespace_name,
                                     cluster_id=db_cluster.id))
            db.session.commit()
            self.log.info('namespace %s created', namespace_name)
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()

        validation_name = item['metric']['__name__']
        validation_status = item['value'][1]
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
            .filter_by(name=objectkind).first()

        validation_context = item['metric']['name']
        db_deploymentvalidation = db.session.query(DeploymentValidation) \
            .filter_by(name=validation_context,
                       tokens_id=db_token.id,
                       namespace_id=db_namespace.id,
                       objectkind_id=db_objectkind.id,
                       validation_id=db_validation.id).first()
        if db_deploymentvalidation is None:
            db.session.add(DeploymentValidation(
                name=validation_context,
                tokens_id=db_token.id,
                namespace_id=db_namespace.id,
                objectkind_id=db_objectkind.id,
                validation_id=db_validation.id
            ))
            db.session.commit()
            self.log.info('deploymentvalidation %s created ',
                          validation_context)

    def get_deploymentvalidations(self):
        """
        SELECT tokens.id AS token_id,
        tokens.creation_timestamp AS token_timestamp
        FROM tokens, deploymentvalidation, namespace, cluster
        WHERE deploymentvalidation.token_id = latest_token.id
        AND deploymentvalidation.namespace_id = namespace.id
        AND namespace.cluster_id = cluster.id
        AND cluster.name = %(name_1)s
        ORDER BY tokens.creation_timestamp DESC
        """
        token = db.session.query(Tokens) \
            .filter(Tokens.id == LatestTokens.token_id,
                    Tokens.data_type == DataTypes.DVODataType,
                    DeploymentValidation.tokens_id == Tokens.id,
                    DeploymentValidation.namespace_id == Namespace.id,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster) \
            .order_by(Tokens.creation_timestamp.desc()) \
            .limit(1) \
            .first()
        if token is None:
            self.log.error('did not find cluster %s', self.cluster)
            return []

        validations = db.session.query(DeploymentValidation) \
            .filter(Validation.id == DeploymentValidation.validation_id,
                    DeploymentValidation.tokens_id == token.id,
                    DeploymentValidation.namespace_id == Namespace.id,
                    DeploymentValidation.objectkind_id == ObjectKind.id,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster).all()

        result = list()
        for validation in validations:
            result.append({'cluster': validation.namespace.cluster.name,
                           'namespace': validation.namespace.name,
                           'validation': validation.validation.name,
                           'context': validation.name,
                           'context-type': validation.objectkind.name,
                           'status': validation.validation.status
                           })
        return result

    @staticmethod
    def get_deploymentvalidation_summary():
        """
        select cluster.name, max(token.id)
        from token, deploymentvalidation, namespace, cluster,
        where token.id = deploymentvalidation.token_id
        and deploymentvalidation.namespace_id = namespace.id
        and namespace.cluster_id = cluster.id
        group by cluster.name
        """

        token = db.session.query(Tokens).filter(
            Tokens.id == LatestTokens.token_id,
            Tokens.data_type == DataTypes.DVODataType,
            Tokens.id == DeploymentValidation.tokens_id,
            DeploymentValidation.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id
        )

        results = db.session.query(
            Cluster,
            Namespace,
            DeploymentValidation,
            Validation,
            func.count(Validation.name).label('Count')
        ).filter(
            DeploymentValidation.validation_id == Validation.id,
            DeploymentValidation.tokens_id == Tokens.id,
            DeploymentValidation.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id,
            Tokens.id == token[0].id
        ).group_by(
            Validation, Namespace, Cluster, DeploymentValidation.id
        )

        return results
