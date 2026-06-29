import os

from flask import Flask
from flask_migrate import Migrate
from flask_healthz import healthz, HealthError  # type: ignore  # noqa: F401
from connexion import App
from connexion.resolver import RestyResolver
from sqlalchemy import text

from dashdotdb.models.base import db
from dashdotdb.models import dashdotdb  # type: ignore  # noqa: F401


DATABASE_URL = os.environ.get('DASHDOTDB_DATABASE_URL')
if DATABASE_URL is None:
    DATABASE_HOST = os.environ.get('DATABASE_HOST')
    DATABASE_PORT = os.environ.get('DATABASE_PORT')
    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    if all((DATABASE_HOST, DATABASE_PORT,
            DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)):
        DATABASE_URL = (f'postgresql://{DATABASE_USERNAME}:'
                        f'{DATABASE_PASSWORD}@'
                        f'{DATABASE_HOST}:'
                        f'{DATABASE_PORT}/'
                        f'{DATABASE_NAME}')

# In-memory SQLite fallback: Flask 3.x imports the app module before
# processing --help, so the module must not crash when no database is
# configured. Real operations fail at connection time.
DATABASE_URL = DATABASE_URL or 'sqlite://'


class DashDotDb(App):
    @staticmethod
    def liveness():
        pass

    @staticmethod
    def readiness():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
        except Exception as error:
            raise HealthError("Can't connect to the database") from error

    def create_app(self):
        # pylint: disable=redefined-outer-name
        app = Flask(self.import_name, **self.server_args)
        app.register_blueprint(healthz, url_prefix="/api/healthz")
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        # pylint: disable=unused-variable
        migrate = Migrate(app, db)  # type: ignore  # noqa: F841
        app.config['HEALTHZ'] = {
            "live": self.liveness,
            "ready": self.readiness,
        }
        return app


conn_app = DashDotDb('dashdotdb', specification_dir='schemas')
conn_app.add_api('swagger.yaml',
                 resolver=RestyResolver('dashdotdb.controllers'))
app = conn_app.app  # pylint: disable=unused-variable
