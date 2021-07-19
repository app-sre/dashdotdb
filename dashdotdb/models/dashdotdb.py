from dashdotdb.models.base import db
from dashdotdb.services import DataTypes


class Token(db.Model):

    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    pods = db.relationship('Pod', backref='token')
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='token')
    serviceslo = db.relationship('ServiceSLO', backref='token')


class Tokens(db.Model):

    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36))
    data_type = db.Column(db.Enum(DataTypes))
    creation_timestamp = db.Column(db.DateTime)
    is_open = db.Column(db.Boolean)
    pods = db.relationship('Pod', backref='tokens')
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='tokens')
    serviceslo = db.relationship('ServiceSLO', backref='tokens')


class LatestTokens(db.Model):

    __tablename__ = 'latesttokens'

    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))


class Pod(db.Model):

    __tablename__ = 'pod'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'))
    tokens_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))


class Namespace(db.Model):

    __tablename__ = 'namespace'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    pods = db.relationship('Pod', backref='namespace')
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='namespace')
    serviceslo = db.relationship('ServiceSLO', backref='namespace')


class Cluster(db.Model):

    __tablename__ = 'cluster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    namespaces = db.relationship('Namespace', backref='cluster')


class Service(db.Model):

    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    serviceslo = db.relationship('ServiceSLO', backref='service')


class ImageFeature(db.Model):

    __tablename__ = 'imagefeature'

    image_id = db.Column(db.Integer, db.ForeignKey('image.id'),
                         primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'),
                           primary_key=True)


class Image(db.Model):

    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    manifest = db.Column(db.String(1000), unique=False)
    features = db.relationship('Feature', secondary='imagefeature')
    pods = db.relationship('Pod', backref='image')


class Feature(db.Model):

    __tablename__ = 'feature'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    namespacename = db.Column(db.String(64), unique=False)
    version = db.Column(db.String(64), unique=False)
    versionformat = db.Column(db.String(64), unique=False)
    images = db.relationship('Image', secondary='imagefeature')
    vulnerabilities = db.relationship('Vulnerability', backref='feature')


class Vulnerability(db.Model):

    __tablename__ = 'vulnerability'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    description = db.Column(db.String(10000), unique=False)
    fixedby = db.Column(db.String(10000), unique=False)
    link = db.Column(db.String(10000), unique=False)
    severity_id = db.Column(db.Integer, db.ForeignKey('severity.id'))
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'))


class Severity(db.Model):

    __tablename__ = 'severity'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    vulnerabilities = db.relationship('Vulnerability', backref='severity')


class DeploymentValidation(db.Model):

    __tablename__ = 'deploymentvalidation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False)
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'))
    tokens_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'))
    objectkind_id = db.Column(db.Integer, db.ForeignKey('objectkind.id'))
    validation_id = db.Column(db.Integer, db.ForeignKey('validation.id'))


class Validation(db.Model):

    __tablename__ = 'validation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    status = db.Column(db.Integer, unique=False)
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='validation')


class ObjectKind(db.Model):

    __tablename__ = 'objectkind'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='objectkind')


class SLIType(db.Model):

    __tablename__ = 'slitype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    serviceslo = db.relationship('ServiceSLO', backref='slitype')


class ServiceSLO(db.Model):

    __tablename__ = 'serviceslo'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    value = db.Column(db.Integer, unique=False)
    target = db.Column(db.Integer, unique=False)
    slitype_id = db.Column(db.Integer, db.ForeignKey('slitype.id'))
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'))
    tokens_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'))
