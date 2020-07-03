from dashdotdb.models.base import db


class Token(db.Model):

    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    pods = db.relationship('Pod', backref='token')


class Pod(db.Model):

    __tablename__ = 'pod'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=False)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'))


class Namespace(db.Model):

    __tablename__ = 'namespace'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    pods = db.relationship('Pod', backref='namespace')


class Cluster(db.Model):

    __tablename__ = 'cluster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    namespaces = db.relationship('Namespace', backref='cluster')


class ImageFeature(db.Model):

    __tablename__ = 'imagefeature'

    image_id = db.Column(db.Integer, db.ForeignKey('image.id'),
                         primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'),
                           primary_key=True)


class Image(db.Model):

    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    manifest = db.Column(db.String(1000), index=True, unique=False)
    features = db.relationship('Feature', secondary='imagefeature')
    pods = db.relationship('Pod', backref='image')


class Feature(db.Model):

    __tablename__ = 'feature'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    namespacename = db.Column(db.String(64), index=True, unique=False)
    version = db.Column(db.String(64), index=True, unique=False)
    versionformat = db.Column(db.String(64), index=True, unique=False)
    images = db.relationship('Image', secondary='imagefeature')
    vulnerabilities = db.relationship('Vulnerability', backref='feature')


class Vulnerability(db.Model):

    __tablename__ = 'vulnerability'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    description = db.Column(db.String(10000), index=True, unique=False)
    fixedby = db.Column(db.String(10000), index=True, unique=False)
    link = db.Column(db.String(10000), index=True, unique=False)
    severity_id = db.Column(db.Integer, db.ForeignKey('severity.id'))
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'))


class Severity(db.Model):

    __tablename__ = 'severity'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    vulnerabilities = db.relationship('Vulnerability', backref='severity')
