from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Token(Base):

    __tablename__ = 'token'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    pods = relationship('Pod', backref='token')


class Pod(Base):

    __tablename__ = 'pod'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=False)
    namespace_id = Column(Integer, ForeignKey('namespace.id'))
    image_id = Column(Integer, ForeignKey('image.id'))
    token_id = Column(Integer, ForeignKey('token.id'))


class Namespace(Base):

    __tablename__ = 'namespace'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=False)
    cluster_id = Column(Integer, ForeignKey('cluster.id'))
    pods = relationship('Pod', backref='namespace')


class Cluster(Base):

    __tablename__ = 'cluster'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    namespaces = relationship('Namespace', backref='cluster')


class ImageFeature(Base):

    __tablename__ = 'imagefeature'

    image_id = Column(Integer, ForeignKey('image.id'), primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.id'), primary_key=True)


class Image(Base):

    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=False)
    manifest = Column(String(1000), index=True, unique=False)
    features = relationship('Feature', secondary='imagefeature')
    pods = relationship('Pod', backref='image')


class Feature(Base):

    __tablename__ = 'feature'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=False)
    namespacename = Column(String(64), index=True, unique=False)
    version = Column(String(64), index=True, unique=False)
    versionformat = Column(String(64), index=True, unique=False)
    images = relationship('Image', secondary='imagefeature')
    vulnerabilities = relationship('Vulnerability', backref='feature')


class Vulnerability(Base):

    __tablename__ = 'vulnerability'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=False)
    description = Column(String(10000), index=True, unique=False)
    fixedby = Column(String(10000), index=True, unique=False)
    link = Column(String(10000), index=True, unique=False)
    severity_id = Column(Integer, ForeignKey('severity.id'))
    feature_id = Column(Integer, ForeignKey('feature.id'))


class Severity(Base):

    __tablename__ = 'severity'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    vulnerabilities = relationship('Vulnerability', backref='severity')
