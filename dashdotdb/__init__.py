import os

from flask import Flask
from flask_migrate import Migrate
from connexion import App
from connexion.resolver import RestyResolver

from dashdotdb.models.base import db
from dashdotdb.models import imagemanifestvuln  # type: ignore  # noqa: F401


DATABASE_URL = os.environ['DASHDOTDB_DATABASE_URL']


class DashDotDb(App):
    def create_app(self):
        # pylint: disable=redefined-outer-name
        app = Flask(self.import_name, **self.server_args)
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        # pylint: disable=unused-variable
        migrate = Migrate(app, db)  # type: ignore  # noqa: F841
        return app


conn_app = DashDotDb(__name__, specification_dir='schemas')
conn_app.add_api('swagger.yaml',
                 resolver=RestyResolver('dashdotdb.controllers'))
app = conn_app.app  # pylint: disable=unused-variable
