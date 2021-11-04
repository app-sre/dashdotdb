import os

from flask import Flask
from flask_migrate import Migrate
from flask_healthz import healthz, HealthError
from connexion import App
from connexion.resolver import RestyResolver

from dashdotdb.models.base import db
from dashdotdb.models import dashdotdb  # type: ignore  # noqa: F401


DATABASE_URL = os.environ.get('DASHDOTDB_DATABASE_URL')
if DATABASE_URL is None:
    DATABASE_HOST = os.environ['DATABASE_HOST']
    DATABASE_PORT = os.environ['DATABASE_PORT']
    DATABASE_USERNAME = os.environ['DATABASE_USERNAME']
    DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
    DATABASE_NAME = os.environ['DATABASE_NAME']
    DATABASE_URL = (f'postgresql://{DATABASE_USERNAME}:'
                    f'{DATABASE_PASSWORD}@'
                    f'{DATABASE_HOST}:'
                    f'{DATABASE_PORT}/'
                    f'{DATABASE_NAME}')


class DashDotDb(App):
    def liveness(self):
        pass

    def readiness(self):
        try:
            db.engine.execute('SELECT 1')
        except Exception:
            raise HealthError("Can't connect to the database")

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
