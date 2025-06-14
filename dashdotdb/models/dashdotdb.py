from dashdotdb.models.base import db
from dashdotdb.models.base import Model
from dashdotdb.services import DataTypes


class Token(Model):

    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    uuid = db.Column(db.String(36), index=True)
    data_type = db.Column(db.Enum(DataTypes))
    is_open = db.Column(db.Boolean, default=False)
    pods = db.relationship('Pod', backref='token')
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='token')
    serviceslo = db.relationship('ServiceSLO', backref='token')


class LatestTokens(Model):

    __tablename__ = 'latesttokens'

    id = db.Column(db.Integer, primary_key=True)
    # no index here, this is a very small table that won't almost grow
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'))


class Pod(Model):

    __tablename__ = 'pod'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False, index=True)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'),
                             index=True)
    images = db.relationship(
        'Image', secondary='podimage', back_populates='pods'
        )
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'),
                         index=True)


class Namespace(Model):

    __tablename__ = 'namespace'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, index=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'), index=True)
    pods = db.relationship('Pod', backref='namespace')
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='namespace')
    serviceslo = db.relationship('ServiceSLO', backref='namespace')


class Cluster(Model):

    __tablename__ = 'cluster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    namespaces = db.relationship('Namespace', backref='cluster')


class Service(Model):

    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    serviceslo = db.relationship('ServiceSLO', backref='service')


class ImageFeature(Model):

    __tablename__ = 'imagefeature'

    image_id = db.Column(db.Integer, db.ForeignKey('image.id'),
                         primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'),
                           primary_key=True)


class Image(Model):

    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=False)
    manifest = db.Column(db.String(1000), unique=False)
    features = db.relationship('Feature', secondary='imagefeature',
                               back_populates='images')
    pods = db.relationship(
        'Pod', secondary='podimage', back_populates='images'
        )

    # Indexes
    __table_args__ = (
        db.Index('ix_image_name_manifest', name, manifest),
    )


class PodImage(Model):

    __tablename__ = 'podimage'

    pod_id = db.Column(db.Integer, db.ForeignKey('pod.id'),
                       primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'),
                         primary_key=True)


class Feature(Model):

    __tablename__ = 'feature'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    version = db.Column(db.String(64), unique=False)
    images = db.relationship('Image', secondary='imagefeature',
                             back_populates='features')
    vulnerabilities = db.relationship('Vulnerability', backref='feature')

    # Indexes
    __table_args__ = (
        db.Index('ix_feature_name_version',
                 name, version),
    )


class Vulnerability(Model):

    __tablename__ = 'vulnerability'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), unique=False, index=True)
    description = db.Column(db.String(10000), unique=False)
    namespacename = db.Column(db.String(128), unique=False)
    fixedby = db.Column(db.String(10000), unique=False)
    link = db.Column(db.String(10000), unique=False)
    # No index in severity_id as we have a very small subset of severities
    severity_id = db.Column(db.Integer, db.ForeignKey('severity.id'))
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'), index=True)

    # We may need another index here because we query this table using name,
    # description, fixedby and link. Since they are so big, it needs to be a
    # functional index computing a hash (e.g. md5) of the column and the
    # related queries to this table need to be modified to use it. Anyway,
    # the index on name is going to help a lot to that four columns query, so
    # the multicolumn index won't probably be needed as long as names don't get
    # repeated often.


class Severity(Model):

    __tablename__ = 'severity'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    vulnerabilities = db.relationship('Vulnerability', backref='severity')


class DeploymentValidation(Model):

    __tablename__ = 'deploymentvalidation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False, index=True)
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'), index=True)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'),
                             index=True)
    # No index in objectkind_id as we have a very small subset of them
    objectkind_id = db.Column(db.Integer, db.ForeignKey('objectkind.id'))
    validation_id = db.Column(db.Integer, db.ForeignKey('validation.id'),
                              index=True)


class Validation(Model):

    __tablename__ = 'validation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    status = db.Column(db.Integer, unique=False)
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='validation')


class ObjectKind(Model):

    __tablename__ = 'objectkind'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='objectkind')


class SLIType(Model):

    __tablename__ = 'slitype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    serviceslo = db.relationship('ServiceSLO', backref='slitype')


class SLODoc(Model):

    __tablename__ = 'slodoc'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    serviceslo = db.relationship('ServiceSLO', backref='slodoc')


class ServiceSLO(Model):

    __tablename__ = 'serviceslo'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, index=True)
    value = db.Column(db.Float, unique=False, nullable=False)
    target = db.Column(db.Float, unique=False, nullable=False)
    # no index, slitype is a very small table
    slitype_id = db.Column(db.Integer, db.ForeignKey('slitype.id'))
    slodoc_id = db.Column(db.Integer, db.ForeignKey('slodoc.id'), index=True)
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'), index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), index=True)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'),
                             index=True)


class DORADeployment(Model):

    __tablename__ = 'doradeployment'
    __table_args__ = (
        db.UniqueConstraint(
            "app_name",
            "env_name",
            "pipeline",
            "trigger_reason",
            name="doradeployment_trigger_reason_app_name_env_name_pipeline_uc",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    trigger_reason = db.Column(db.String(256), unique=False, index=True)

    # timestamp of the deployment event (not of the DB entry). It should
    # be as close as possible to the end of the pipeline.
    finish_timestamp = db.Column(db.DateTime, index=True)

    app_name = db.Column(db.String(256), unique=False, index=True)
    env_name = db.Column(db.String(256), unique=False, index=True)
    pipeline = db.Column(db.String(256), unique=False, index=True)


class DORACommit(Model):

    __tablename__ = 'doracommit'
    __table_args__ = (db.UniqueConstraint('deployment_id', 'revision',
                      'repo', name='doracommit_depid_rev_repo_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    deployment_id = db.Column(db.Integer, db.ForeignKey(
        'doradeployment.id'), index=True)

    # timestamp of the commit event (not of the DB entry)
    timestamp = db.Column(db.DateTime, index=True)

    revision = db.Column(db.String(40), unique=False)
    repo = db.Column(db.String(256), unique=False)

    lttc = db.Column(db.Interval)
