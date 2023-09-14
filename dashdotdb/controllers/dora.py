from typing import Any, Union

from dashdotdb.services.dora import DORA, DORAInsertStats
from dashdotdb.controllers.token import (
    TokenNotFound,
    TOKEN_NOT_FOUND_CODE,
    TOKEN_NOT_FOUND_MSG,
)


def post(user, body) -> Union[tuple[str, int], tuple[DORAInsertStats, int]]:
    try:
        stats = DORA().insert(token=user, manifest=body)
    except TokenNotFound:
        return TOKEN_NOT_FOUND_MSG, TOKEN_NOT_FOUND_CODE

    # if there's at least one entry created (or marked as duplicate), then this
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
