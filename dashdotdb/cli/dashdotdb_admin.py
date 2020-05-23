import argparse
import logging
import sys

from dashdotdb import Session
from dashdotdb.db.db import engine
from dashdotdb.db.stored_procedures import VULNERABILITIES_DROP
from dashdotdb.db.stored_procedures import VULNERABILITIES_CREATE
from dashdotdb.db.model import Base


APP_LOG = logging.getLogger('app')
APP_LOG_HANDLER = logging.StreamHandler(sys.stdout)
APP_LOG_HANDLER.setFormatter(logging.Formatter(fmt='%(message)s'))
APP_LOG.addHandler(APP_LOG_HANDLER)
APP_LOG.setLevel(logging.INFO)


class DashDotDBAdmin:
    def __init__(self):
        parser = argparse.ArgumentParser(prog='dashdotdb-admin')

        subcommands = parser.add_subparsers(title='subcommands',
                                            help='subcommand help',
                                            dest='subcommand')

        subcommands.add_parser('initdb')
        subcommands.add_parser('resetdb')

        self.args = parser.parse_args()

    def run(self):
        if self.args.subcommand == 'resetdb':
            APP_LOG.info('Creating tables')
            Base.metadata.create_all(engine)
            APP_LOG.info('Creating stored procedures')
            Session.execute(VULNERABILITIES_CREATE)
            Session.commit()

        if self.args.subcommand == 'resetdb':
            APP_LOG.info('(re)Creating tables')
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            APP_LOG.info('(re)Creating stored procedures')
            Session.execute(VULNERABILITIES_DROP)
            Session.execute(VULNERABILITIES_CREATE)
            Session.commit()


def main():
    cli = DashDotDBAdmin()
    cli.run()
