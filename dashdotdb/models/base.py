from typing import TYPE_CHECKING
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = db.Model
