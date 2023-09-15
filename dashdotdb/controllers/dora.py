from typing import Any, Union

from dashdotdb.services.dora import DORA, DORAInsertStats


def post(body) -> Union[tuple[str, int], tuple[DORAInsertStats, int]]:
    stats = DORA().insert(manifest=body)

    # if there's at least one entry created (or marked as duplicate), then
    # the post has been successful, but we report the errors.
    if stats.created or stats.duplicated:
        code = 201
    else:
        code = 400

    return stats, code


def latest_deployment(
    app_name, env_name
) -> Union[tuple[str, int], tuple[dict[str, Any], int]]:
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
