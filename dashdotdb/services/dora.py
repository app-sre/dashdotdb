import logging
import datetime

from jsonschema import validate, ValidationError

# from sqlalchemy import func

from dashdotdb.models.dashdotdb import (
    db,
    Token,
    DataTypes,
    # LatestTokens,
    DORADeployment,
    DORACommit
)

from dashdotdb.controllers.token import (TOKEN_NOT_FOUND_CODE,
                                         TOKEN_NOT_FOUND_MSG)


class DORA:
    def __init__(self):
        self.log = logging.getLogger()

    def insert(self, token, manifest):

        db_token = db.session.query(Token) \
            .filter(Token.uuid == token,
                    Token.data_type == DataTypes.DORADataType).first()

        if db_token is None:
            self.log.error(
                'skipping validation: %s %s', TOKEN_NOT_FOUND_MSG, token)
            return TOKEN_NOT_FOUND_MSG, TOKEN_NOT_FOUND_CODE

        schema = {
                "type": "object",
                "properties": {
                    "deployments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "trigger_reason": {
                                    "type": "string",
                                    # TODO: Maybe relax pattern?
                                    "pattern": r'https://gitlab\.cee\.redhat\.com/service/.*/commit/.*'
                                    },
                                "finish_timestamp": {
                                    "type": "string",
                                    # RFC 3339, optional 'T' separator
                                    "pattern": r'^((?:(\d{4}-\d{2}-\d{2})(T| )(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$'
                                    },
                                "app_name": {"type": "string"},
                                "env_name": {"type": "string"},
                                "pipeline": {"type": "string"},
                                "commits": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "revision": {
                                                "type": "string",
                                                "pattern": r'[a-f0-9]{40}',
                                                },
                                            "timestamp": {
                                                "type": "string",
                                                "pattern": r'^((?:(\d{4}-\d{2}-\d{2})(T| )(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$'
                                                },
                                            "repo": {
                                                "type": "string",
                                                # TODO: Maybe relax pattern?
                                                "pattern": r'https://git.*\.com/.*/.*',
                                                },
                                            }
                                        }
                                    },
                                }
                            },
                        }
                    }
                }

        try:
            validate(instance=manifest, schema=schema)
        except ValidationError as e:
            print("Invalid JSON: ", e)
            return "bad request", 400

        for dep_data in manifest["deployments"]:
            finish_timestamp = datetime.datetime.fromisoformat(
                dep_data['finish_timestamp'])

            # finish_timestamp and timestamp may come offset-naive or offset-aware, and
            # they can't be subtracted if they are different. Converting always
            # to offset-aware. If no TZ data is provided, we assume UTC.
            if finish_timestamp.tzinfo is None:
                finish_timestamp = finish_timestamp.replace(
                    tzinfo=datetime.timezone.utc)

            deployment = DORADeployment(
                token_id=db_token.id,
                finish_timestamp=finish_timestamp,
                trigger_reason=dep_data['trigger_reason'],
                app_name=dep_data['app_name'],
                env_name=dep_data['env_name'],
                pipeline=dep_data['pipeline'],
            )
            db.session.add(deployment)
            db.session.commit()

            for commit_data in dep_data["commits"]:
                timestamp = datetime.datetime.fromisoformat(commit_data['timestamp'])
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

                lttc = finish_timestamp - timestamp
                commit = DORACommit(
                    deployment_id=deployment.id,
                    timestamp=datetime.datetime.fromisoformat(commit_data['timestamp']),
                    revision=commit_data['revision'],
                    repo=commit_data['repo'],
                    lttc=lttc
                )
                db.session.add(commit)

        db.session.commit()

        return "ok", 200

    def get_latest_deployment(self, app_name, env_name, pipeline):
        return db.session.query(DORADeployment).filter_by(
            app_name=app_name,
            env_name=env_name,
            pipeline=pipeline,
        ).order_by(DORADeployment.finish_timestamp.desc()).first()
