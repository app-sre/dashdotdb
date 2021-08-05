import logging

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Token
from dashdotdb.models.dashdotdb import LatestTokens
from dashdotdb.models.dashdotdb import Service
from dashdotdb.models.dashdotdb import Cluster
from dashdotdb.models.dashdotdb import Namespace
from dashdotdb.models.dashdotdb import ServiceSLO
from dashdotdb.models.dashdotdb import SLIType
from dashdotdb.services import DataTypes
from dashdotdb.controllers.token import (TOKEN_NOT_FOUND_CODE,
                                         TOKEN_NOT_FOUND_MSG)


class ServiceSLOMetrics:
    def __init__(self, cluster=None, namespace=None, sli_type=None, name=None):
        self.log = logging.getLogger()

        self.cluster = cluster
        self.namespace = namespace
        self.sli_type = sli_type
        self.name = name

    def insert(self, token, slo):

        db_token = db.session.query(Token) \
            .filter(Token.uuid == token,
                    Token.data_type == DataTypes.SLODataType).first()
        if db_token is None:
            self.log.error(
                f'skipping service SLO: {TOKEN_NOT_FOUND_MSG} {token}')
            return TOKEN_NOT_FOUND_MSG, TOKEN_NOT_FOUND_CODE

        service_name = slo['service']['name']
        db_service = db.session.query(Service) \
            .filter_by(name=service_name).first()
        if db_service is None:
            db.session.add(Service(name=service_name))
            db.session.commit()
            self.log.info('service %s created', service_name)
        db_service = db.session.query(Service) \
            .filter_by(name=service_name).first()

        cluster_name = slo['cluster']['name']
        db_cluster = db.session.query(Cluster) \
            .filter_by(name=cluster_name).first()
        if db_cluster is None:
            db.session.add(Cluster(name=cluster_name))
            db.session.commit()
            self.log.info('cluster %s created', cluster_name)
        db_cluster = db.session.query(Cluster) \
            .filter_by(name=cluster_name).first()

        namespace_name = slo['namespace']['name']
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()
        if db_namespace is None:
            db.session.add(Namespace(name=namespace_name,
                                     cluster_id=db_cluster.id))
            db.session.commit()
            self.log.info('namespace %s created', namespace_name)
        db_namespace = db.session.query(Namespace) \
            .filter_by(name=namespace_name, cluster_id=db_cluster.id).first()

        slitype_name = slo['SLIType']
        db_slitype = db.session.query(SLIType) \
            .filter_by(name=slitype_name).first()
        if db_slitype is None:
            db.session.add(SLIType(name=slitype_name))
            db.session.commit()
            self.log.info('slitype %s created', slitype_name)
        db_slitype = db.session.query(SLIType) \
            .filter_by(name=slitype_name).first()

        db_serviceslo = db.session.query(ServiceSLO) \
            .filter_by(name=slo['name'],
                       service_id=db_service.id,
                       namespace_id=db_namespace.id,
                       slitype_id=db_slitype.id,
                       token_id=db_token.id).first()
        if db_serviceslo is None:
            db.session.add(ServiceSLO(name=slo['name'],
                                      service_id=db_service.id,
                                      namespace_id=db_namespace.id,
                                      slitype_id=db_slitype.id,
                                      token_id=db_token.id))
            db.session.commit()
            self.log.info('ServiceSLO %s created ', slo['name'])
        db_serviceslo = db.session.query(ServiceSLO) \
            .filter_by(name=slo['name'],
                       service_id=db_service.id,
                       namespace_id=db_namespace.id,
                       slitype_id=db_slitype.id,
                       token_id=db_token.id).first()
        db_serviceslo.value = slo['value']
        db_serviceslo.target = slo['target']
        db.session.commit()
        self.log.info('ServiceSLO %s updated ', slo['name'])

    def get_slometrics(self):
        token = db.session.query(Token) \
            .filter(Token.id == LatestTokens.token_id,
                    Token.data_type == DataTypes.SLODataType,
                    ServiceSLO.token_id == Token.id,
                    ServiceSLO.namespace_id == Namespace.id,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster,
                    ServiceSLO.name == self.name) \
            .order_by(Token.timestamp.desc()) \
            .limit(1) \
            .first()

        if token is None:
            return []

        serviceslo = db.session.query(ServiceSLO) \
            .filter(ServiceSLO.token_id == token.id,
                    ServiceSLO.slitype_id == SLIType.id,
                    SLIType.name == self.sli_type,
                    ServiceSLO.namespace_id == Namespace.id,
                    Namespace.name == self.namespace,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == self.cluster,
                    ServiceSLO.name == self.name
                    ).first()

        if serviceslo is None:
            return []

        sli_type = db.session.query(SLIType) \
            .filter(ServiceSLO.slitype_id == SLIType.id).first()
        service = db.session.query(Service) \
            .filter(ServiceSLO.service_id == Service.id).first()
        namespace = db.session.query(Namespace) \
            .filter(ServiceSLO.namespace_id == Namespace.id).first()
        cluster = db.session.query(Cluster) \
            .filter(Namespace.id == namespace.id,
                    Namespace.cluster_id == Cluster.id).first()

        result = {
            'name': serviceslo.name,
            'sli_type': sli_type.name,
            'value': serviceslo.value,
            'target': serviceslo.target,
            'service': service.name,
            'cluster': cluster.name,
            'namespace': namespace.name
        }

        return result

    @staticmethod
    def get_slometrics_summary():
        token = db.session.query(Token).filter(
            Token.id == LatestTokens.token_id,
            Token.data_type == DataTypes.SLODataType,
            ServiceSLO.token_id == Token.id,
            ServiceSLO.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id
        )

        results = db.session.query(
            Cluster,
            Namespace,
            Service,
            ServiceSLO,
            SLIType
        ).filter(
            ServiceSLO.slitype_id == SLIType.id,
            ServiceSLO.token_id == Token.id,
            ServiceSLO.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id,
            Token.id == token[0].id
        ).group_by(
            SLIType, Namespace, Cluster, ServiceSLO, Service
        )

        return results
