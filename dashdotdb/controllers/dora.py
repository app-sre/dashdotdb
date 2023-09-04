from psycopg2.errors import UniqueViolation
from sqlalchemy import exc

from dashdotdb.services.dora import DORA

def post(user, body):
    try:
        msg, code = DORA().insert(token=user, manifest=body)
    except exc.IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            return "UniqueViolation. Data already exists in DB.", 409
        raise(e)
    return msg, code
