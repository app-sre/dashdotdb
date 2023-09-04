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

def latest_deployment(app_name, env_name, pipeline):
    deployment = DORA().get_latest_deployment(app_name, env_name, pipeline)
    if deployment is None:
        return "Not found", 404

    response = {
        "app_name": deployment.app_name,
        "env_name": deployment.env_name,
        "pipeline": deployment.pipeline,
        "finish_timestamp": deployment.finish_timestamp,
        "trigger_reason": deployment.trigger_reason,
    }

    return response, 200
