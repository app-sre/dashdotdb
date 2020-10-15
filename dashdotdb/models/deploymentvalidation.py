from dashdotdb.models.base import db


class Token(db.Model):

    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    deploymentvalidation = db.relationship('DeploymentValidation', backref='token')


class DeploymentValidation(db.Model):

    __tablename__ = 'DeploymentValidation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False)
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'))
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'))
    objectkind_id = db.Column(db.Integer, db.ForeignKey('objectkind.id'))
    validation_id = db.Column(db.Integer, db.ForeignKey('validation.id'))
    status = db.Column(db.Integer, unique=False))


class Namespace(db.Model):

    __tablename__ = 'namespace'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    deploymentvalidation = db.relationship('DeploymentValidation', backref='namespace')


class Cluster(db.Model):

    __tablename__ = 'cluster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    namespaces = db.relationship('Namespace', backref='cluster')


class Validation(db.Model):

    __tablename__ = 'validation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    deploymentvalidation = db.relationship('DeploymentValidation', backref='validation')


class ObjectKind(db.Model):

    __tablename__ = 'objectkind'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    deploymentvalidation = db.relationship('deploymentvalidation', backref='objectkind')
