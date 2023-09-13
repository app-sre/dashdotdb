import logging
import datetime

from psycopg2.errors import UniqueViolation
from sqlalchemy import exc

from dashdotdb.models.dashdotdb import db, Token, DataTypes, DORADeployment, DORACommit
from dashdotdb.controllers.token import TOKEN_NOT_FOUND_CODE, TOKEN_NOT_FOUND_MSG


class DORA:
    def __init__(self):
        self.log = logging.getLogger()

    def insert(self, token, manifest):
        db_token = (
            db.session.query(Token)
            .filter(Token.uuid == token, Token.data_type == DataTypes.DORADataType)
            .first()
        )

        if db_token is None:
            self.log.error("skipping validation: %s %s", TOKEN_NOT_FOUND_MSG, token)
            return TOKEN_NOT_FOUND_MSG, TOKEN_NOT_FOUND_CODE

        stats = {
            "committed": [],
            "duplicate": [],
            "error": [],
        }

        for dep_data in manifest["deployments"]:
            # start transaction - we want to do an atomic
            # transaction of deployment and commits
            db.session.begin_nested()

            dep_short_name = (
                "app_name={},env_name={},pipeline={},trigger_reason={}".format(
                    dep_data["app_name"],
                    dep_data["env_name"],
                    dep_data["pipeline"],
                    dep_data["trigger_reason"],
                )
            )

            try:
                finish_timestamp = datetime.datetime.fromisoformat(
                    dep_data["finish_timestamp"]
                )

                # finish_timestamp and timestamp may come offset-naive or offset-aware,
                # and they can't be subtracted if they are different. Converting always
                # to offset-aware. If no TZ data is provided, we assume UTC.
                if finish_timestamp.tzinfo is None:
                    finish_timestamp = finish_timestamp.replace(
                        tzinfo=datetime.timezone.utc
                    )

                deployment = DORADeployment(
                    token_id=db_token.id,
                    finish_timestamp=finish_timestamp,
                    trigger_reason=dep_data["trigger_reason"],
                    app_name=dep_data["app_name"],
                    env_name=dep_data["env_name"],
                    pipeline=dep_data["pipeline"],
                )
                db.session.add(deployment)
                db.session.commit()

                for commit_data in dep_data["commits"]:
                    commit = DORACommit(
                        deployment_id=deployment.id,
                        timestamp=datetime.datetime.fromisoformat(
                            commit_data["timestamp"]
                        ),
                        revision=commit_data["revision"],
                        repo=commit_data["repo"],
                        lttc=datetime.timedelta(seconds=commit_data["lttc"]),
                    )
                    db.session.add(commit)
                db.session.commit()
            except Exception as e:
                if isinstance(e, exc.IntegrityError) and isinstance(
                    e.orig, UniqueViolation
                ):
                    stats["duplicate"].append(dep_short_name)
                    self.log.info("DUPLICATE deployment: %s", dep_short_name)
                else:
                    stats["error"].append(dep_short_name)
                    self.log.error("ERROR deployment: %s - %s", dep_short_name, e)

                db.session.rollback()
            else:
                stats["committed"].append(dep_short_name)

        return stats

    def get_latest_deployment(self, app_name, env_name):
        return (
            db.session.query(DORADeployment)
            .filter_by(
                app_name=app_name,
                env_name=env_name,
            )
            .order_by(DORADeployment.finish_timestamp.desc())
            .first()
        )
