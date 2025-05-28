import logging
import datetime
from dataclasses import dataclass, field
from typing import List

from psycopg2.errors import UniqueViolation  # pylint: disable-msg=E0611
from sqlalchemy import exc

from dashdotdb.models.dashdotdb import db, DORADeployment, DORACommit


@dataclass
class DORAInsertStats:
    created: List[str] = field(default_factory=lambda: [])
    duplicated: List[str] = field(default_factory=lambda: [])
    error: List[str] = field(default_factory=lambda: [])


class DORA:
    def __init__(self) -> None:
        self.log = logging.getLogger()

    def insert(self, manifest) -> DORAInsertStats:
        stats = DORAInsertStats()

        for dep_data in manifest["deployments"]:
            # start transaction - we want to do an atomic
            # transaction of deployment and commits
            db.session.begin_nested()

            dep_short_name = (
                f"app_name={dep_data['app_name']},"
                f"env_name={dep_data['env_name']},"
                f"pipeline={dep_data['pipeline']},"
                f"trigger_reason={dep_data['trigger_reason']}"
            )

            try:
                finish_timestamp = datetime.datetime.fromisoformat(
                    dep_data["finish_timestamp"]
                )

                # finish_timestamp and timestamp may come offset-naive
                # or offset-aware,
                # and they can't be subtracted if they are different.
                # Converting always
                # to offset-aware. If no TZ data is provided, we assume UTC.
                if finish_timestamp.tzinfo is None:
                    finish_timestamp = finish_timestamp.replace(
                        tzinfo=datetime.timezone.utc
                    )

                deployment = DORADeployment(
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
            except exc.SQLAlchemyError as exception:
                if isinstance(exception, exc.IntegrityError) and isinstance(
                    exception.orig, UniqueViolation
                ):
                    stats.duplicated.append(dep_short_name)
                    self.log.info("DUPLICATE deployment: %s", dep_short_name)
                else:
                    stats.error.append(dep_short_name)
                    self.log.error(
                        "ERROR deployment: %s - %s", dep_short_name, exception
                    )

                db.session.rollback()
            else:
                stats.created.append(dep_short_name)

        return stats

    def get_latest_deployment(self, app_name, env_name) -> DORADeployment:
        return (
            db.session.query(DORADeployment)
            .filter_by(
                app_name=app_name,
                env_name=env_name,
            )
            .order_by(DORADeployment.finish_timestamp.desc())
            .first()
        )
