import argparse
import datetime
import json
import sys

from collections import defaultdict

from tabulate import tabulate

from dashdotdb import Session
from dashdotdb import Image
from dashdotdb import Cluster
from dashdotdb import Namespace
from dashdotdb import Feature
from dashdotdb import Severity
from dashdotdb import Vulnerability
from dashdotdb import Pod
from dashdotdb import Token

from dashdotdb.cli.plugins_interface import Cmd


class ImageManifestVuln(Cmd):

    description = 'Image Manifest Vulnerability'

    def configure_apply(self, parser):
        parser = super().configure_apply(parser)
        parser.add_argument('-f', '--filename', type=argparse.FileType('r'), nargs='?', default=None,
                            help='that contains the configuration to apply')
        parser.add_argument('infile', type=argparse.FileType('r'), nargs='?', default=None,
                            help='that contains the configuration to apply')
        parser.add_argument('-c', '--cluster', type=str, required=True,
                            help='name of the cluster to reference the configuration')
        parser.add_argument('--delta', type=int, default=2,
                            help='delta time in minutes')

    def configure_get(self, parser):
        parser = super().configure_get(parser)
        parser.add_argument('-c', '--cluster', type=str,)
        parser.add_argument('-n', '--namespace', type=str)
        parser.add_argument('-s', '--severity', type=str)

    def apply(self, args):
        if args.filename is not None and args.infile is not None:
            self.log.error('"--filename" OR "-": pick one')
            sys.exit(1)

        if args.filename is not None:
            data = json.load(args.filename)
        elif args.infile is not None:
            data = json.load(args.infile)
        else:
            self.log.error('input missing: use "--filename" or "-"')
            sys.exit(1)

        if 'items' in data:
            for item in data['items']:
                self.insert_to_database(args=args, manifest=item)
        else:
            self.insert_to_database(args=args, manifest=data)

    def insert_to_database(self, args, manifest):
        if manifest['kind'] != 'ImageManifestVuln':
            self.log.info(f'skipping kind "{manifest["kind"]}"')

        expire = datetime.datetime.now() - datetime.timedelta(minutes=args.delta)
        db_token = Session.query(Token).filter(Token.timestamp > expire).first()
        if db_token is None:
            Session.add(Token(timestamp=datetime.datetime.now()))
            Session.commit()
            self.log.info('token created')
        db_token = Session.query(Token).filter(Token.timestamp > expire).first()

        cluster_name = args.cluster
        db_cluster = Session.query(Cluster).filter_by(name=cluster_name).first()
        if db_cluster is None:
            Session.add(Cluster(name=cluster_name))
            Session.commit()
            self.log.info('cluster %s created', cluster_name)
        db_cluster = Session.query(Cluster).filter_by(name=cluster_name).first()

        namespace_name = manifest['metadata']['namespace']
        db_namespace = Session.query(Namespace).filter_by(name=namespace_name,
                                                          cluster_id=db_cluster.id).first()
        if db_namespace is None:
            Session.add(Namespace(name=namespace_name,
                                  cluster_id=db_cluster.id))
            Session.commit()
            self.log.info('namespace %s created', namespace_name)
        db_namespace = Session.query(Namespace).filter_by(name=namespace_name,
                                                          cluster_id=db_cluster.id).first()

        image_name = manifest['spec']['image']
        image_manifest = manifest['spec']['manifest']
        db_image = Session.query(Image).filter_by(name=image_name, manifest=image_manifest).first()
        if db_image is None:
            Session.add(Image(name=image_name,
                              manifest=image_manifest))
            Session.commit()
            self.log.info('image %s created', image_name)
        db_image = Session.query(Image).filter_by(name=image_name, manifest=image_manifest).first()

        features = manifest['spec']['features']
        for feature in features:
            feature_name = feature['name']
            feature_namespacename = feature['namespaceName']
            feature_version = feature['version']
            feature_versionformat = feature['versionformat']
            db_feature = Session.query(Feature).filter_by(name=feature_name,
                                                          namespacename=feature_namespacename,
                                                          version=feature_version,
                                                          versionformat=feature_versionformat).first()
            if db_feature is None:
                Session.add(Feature(name=feature_name,
                                    namespacename=feature_namespacename,
                                    version=feature_version,
                                    versionformat=feature_versionformat,
                                    images=[db_image]))
                Session.commit()
                self.log.info('feature %s created ', feature_name)
            db_feature = Session.query(Feature).filter_by(name=feature_name,
                                                          namespacename=feature_namespacename,
                                                          version=feature_version,
                                                          versionformat=feature_versionformat).first()

            vulnerabilities = feature['vulnerabilities']
            for vulnerability in vulnerabilities:
                vulnerability_name = vulnerability['name']
                vulnerability_description = vulnerability['description']
                vulnerability_link = vulnerability['link']
                vulnerability_fixedby = vulnerability['fixedby']
                vulnerability_severity = vulnerability['severity']
                db_severity = Session.query(Severity).filter_by(name=vulnerability_severity).first()
                if db_severity is None:
                    Session.add(Severity(name=vulnerability_severity))
                    Session.commit()
                    self.log.info('severity %s created ', vulnerability_severity)
                db_severity = Session.query(Severity).filter_by(name=vulnerability_severity).first()

                db_vulnerability = Session.query(Vulnerability).filter_by(name=vulnerability_name,
                                                                          description=vulnerability_description,
                                                                          fixedby=vulnerability_fixedby,
                                                                          link=vulnerability_link,
                                                                          severity_id=db_severity.id,
                                                                          feature_id=db_feature.id).first()
                if db_vulnerability is None:
                    Session.add(Vulnerability(name=vulnerability_name,
                                              description=vulnerability_description,
                                              fixedby=vulnerability_fixedby,
                                              link=vulnerability_link,
                                              severity_id=db_severity.id,
                                              feature_id=db_feature.id))
                    Session.commit()
                    self.log.info('vulnerability %s created ', vulnerability_name)

        pods = manifest['status']['affectedPods'].keys()
        for pod in pods:
            db_pod = Session.query(Pod).filter_by(name=pod,
                                                  namespace_id=db_namespace.id,
                                                  image_id=db_image.id,
                                                  token_id=db_token.id).first()
            if db_pod is None:
                Session.add(Pod(name=pod,
                                namespace_id=db_namespace.id,
                                image_id=db_image.id,
                                token_id=db_token.id))
                Session.commit()
                self.log.info('pod %s created', pod)

    def get(self, args):
        if args.cluster is None:
            clusters = Session.query(Cluster).all()
            result = {'CLUSTERS': [cluster.name for cluster in clusters]}
            self.log.info(tabulate(result, headers=result.keys()))
            self.log.info('')
            self.log.info('Please use "--cluster" to select a cluster')
            sys.exit()

        if args.namespace is None:
            namespaces = Session.query(Namespace).filter(Namespace.cluster_id == Cluster.id,
                                                         Cluster.name == args.cluster).all()
            result = {'NAMESPACES': [namespace.name for namespace in namespaces]}
            self.log.info(tabulate(result, headers=result.keys()))
            self.log.info('')
            self.log.info('Please use "--namespace" to select a namespace')
            sys.exit()

        token = Session.query(Token) \
            .filter(Pod.token_id == Token.id,
                    Pod.namespace_id == Namespace.id,
                    Namespace.cluster_id == Cluster.id,
                    Cluster.name == args.cluster) \
            .order_by(Token.timestamp.desc()) \
            .limit(1) \
            .first()

        if token is None:
            self.log.info('No results')
            sys.exit()

        images = Session.query(Image).filter(Image.id == Pod.image_id,
                                             Pod.token_id == token.id,
                                             Pod.namespace_id == Namespace.id,
                                             Namespace.name == args.namespace,
                                             Namespace.cluster_id == Cluster.id,
                                             Cluster.name == args.cluster).all()

        result = defaultdict(list)
        for image in images:
            for feature in image.features:
                for vulnerability in feature.vulnerabilities:

                    if args.severity is not None:
                        if vulnerability.severity.name != args.severity:
                            continue

                    result['REPOSITORY'].append(image.name)
                    result['NAME'].append(feature.namespacename)
                    result['MANIFEST'].append(image.manifest[:14])
                    result['AFFECTED_PODS'].append(len(image.pods))
                    result['VULNERABILITY'].append(vulnerability.name)

                    result['SEVERITY'].append(vulnerability.severity.name)

                    result['PACKAGE'].append(feature.name)
                    result['CURRENT_VERSION'].append(feature.version)
                    result['FIXED_IN_VERSION'].append(vulnerability.fixedby)
                    result['LINK'].append(vulnerability.link)

        self.log.info(tabulate(result, headers=result.keys()))
