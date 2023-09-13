from dashdotdb.services.dora import DORA


def post(user, body):
    stats = DORA().insert(token=user, manifest=body)

    if stats['committed'] or stats['duplicate']:
        code = 201
    else:
        code = 400

    return stats, code


def latest_deployment(app_name, env_name):
    deployment = DORA().get_latest_deployment(app_name, env_name)
    if deployment is None:
        return "Not found", 404

    response = {
        "app_name": deployment.app_name,
        "env_name": deployment.env_name,
        "pipeline": deployment.pipeline,
        "finish_timestamp": deployment.finish_timestamp.isoformat(),
        "trigger_reason": deployment.trigger_reason,
    }

    return response, 200
