import logging

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Token
from dashdotdb.models.dashdotdb import LatestTokens
from dashdotdb.models.dashdotdb import Service
from dashdotdb.models.dashdotdb import Cluster
from dashdotdb.models.dashdotdb import Namespace
from dashdotdb.models.dashdotdb import ServiceSLO
from dashdotdb.models.dashdotdb import SLIType
from dashdotdb.models.dashdotdb import SLODoc
from dashdotdb.services import DataTypes
from dashdotdb.controllers.token import (TOKEN_NOT_FOUND_CODE,
                                         TOKEN_NOT_FOUND_MSG)


class ServiceSLOMetrics:
    def __init__(self, cluster=None, namespace=None, sli_type=None, slo_doc=None, name=None):
        self.log = logging.getLogger()

        self.cluster = cluster
        self.namespace = namespace
        self.sli_type = sli_type
        self.slo_doc = slo_doc
        self.name = name

    def insert(self, token, slo):

        db_token = db.session.query(Token) \
            .filter(Token.uuid == token,
                    Token.data_type == DataTypes.SLODataType).first()
        if db_token is None:
            self.log.error(
                'skipping validation: %s %s', TOKEN_NOT_FOUND_MSG, token)
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

        slodoc_name = slo['SLODoc']['name']
        db_slodoc = db.session.query(SLODoc) \
            .filter_by(name=slodoc_name).first()
        if db_slodoc is None:
            db.session.add(SLODoc(name=slodoc_name))
            db.session.commit()
            self.log.info('slodoc %s created', slodoc_name)
        db_slodoc = db.session.query(SLODoc) \
            .filter_by(name=slodoc_name).first()

        db_serviceslo = db.session.query(ServiceSLO) \
            .filter_by(name=slo['name'],
                       service_id=db_service.id,
                       namespace_id=db_namespace.id,
                       slitype_id=db_slitype.id,
                       slodoc_id=db_slodoc.id,
                       token_id=db_token.id).first()
        if db_serviceslo is None:
            db.session.add(ServiceSLO(name=slo['name'],
                                      service_id=db_service.id,
                                      namespace_id=db_namespace.id,
                                      slitype_id=db_slitype.id,
                                      slodoc_id=db_slodoc.id,
                                      token_id=db_token.id,
                                      value=slo['value'],
                                      target=slo['target']))
            db.session.commit()
            self.log.info('ServiceSLO %s created ', slo['name'])

        return "ok", 200

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
                    SLODoc.name == self.slo_doc,
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
        slo_doc = db.session.query(SLODoc) \
            .filter(ServiceSLO.slodoc_id == SLODoc.id).first()
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
            'slo_doc': slo_doc.name,
            'value': serviceslo.value,
            'target': serviceslo.target,
            'service': service.name,
            'cluster': cluster.name,
            'namespace': namespace.name
        }

        return result

    @staticmethod
    def get_slometrics_summary():
        # SELECT token.id, token.timestamp, token.data_type, token.is_open
        # FROM token, latesttokens, serviceslo
        # WHERE token.id = latesttokens.token_id
        # AND token.data_type = 'SLODataType'
        # AND serviceslo.token_id = token.id
        token = db.session.query(Token).filter(
            Token.id == LatestTokens.token_id,
            Token.data_type == DataTypes.SLODataType,
            ServiceSLO.token_id == Token.id,
        ).first()
        if token is None:
            return []

        # SELECT cluster.name, namespace.name, service.name, serviceslo.name,
        # serviceslo.value, serviceslo.target, slitype.name
        # FROM cluster, namespace, service, serviceslo, slitype
        # WHERE serviceslo.slitype_id = slitype.id
        # AND serviceslo.slodoc_id = slodoc.id
        # AND serviceslo.service_id = service.id
        # AND serviceslo.namespace_id = namespace.id
        # AND namespace.cluster_id = cluster.id
        # AND serviceslo.token_id = %(token_id_1)s
        results = db.session.query(
            Cluster,
            Namespace,
            Service,
            ServiceSLO,
            SLIType,
            SLODoc
        ).filter(
            ServiceSLO.slitype_id == SLIType.id,
            ServiceSLO.slodoc_id == SLODoc.id,
            ServiceSLO.service_id == Service.id,
            ServiceSLO.namespace_id == Namespace.id,
            Namespace.cluster_id == Cluster.id,
            ServiceSLO.token_id == token.id
        )

        return results
