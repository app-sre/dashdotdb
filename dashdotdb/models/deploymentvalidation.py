from dashdotdb.models.base import db


class ValidationToken(db.Model):
    __tablename__ = 'validationtoken'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='validationtoken')


class DeploymentValidation(db.Model):
    __tablename__ = 'deploymentvalidation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False)
    token_id = db.Column(db.Integer, db.ForeignKey('validationtoken.id'))
    namespace_id = db.Column(db.Integer, db.ForeignKey('dvnamespace.id'))
    objectkind_id = db.Column(db.Integer, db.ForeignKey('objectkind.id'))
    validation_id = db.Column(db.Integer, db.ForeignKey('validation.id'))


class DVNamespace(db.Model):
    __tablename__ = 'dvnamespace'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    cluster_id = db.Column(db.Integer, db.ForeignKey('dvcluster.id'))
    deploymentvalidation = db.relationship('DeploymentValidation',
                                           backref='namespace')


class DVCluster(db.Model):
    __tablename__ = 'dvcluster'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    namespaces = db.relationship('DVNamespace', backref='cluster')


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
