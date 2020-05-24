import argparse

from dashdotdb.core.version import VERSION


class Parser:

    def __init__(self):
        self.args = argparse.Namespace()
        self.application = argparse.ArgumentParser(prog='dashdotdb',
                                                   description='DashDotDB CLI')
        self.application.add_argument('-v', '--version', action='version',
                                      version='dashdotdb %s' % VERSION)
        self.actions = self.application.add_subparsers(title='actions',
                                                       help='actions help',
                                                       dest='action',
                                                       required=True)

        apply = self.actions.add_parser('apply')
        self.apply_subparsers = apply.add_subparsers(title='plugins',
                                                     help='help',
                                                     dest='plugin',
                                                     required=True)

        get = self.actions.add_parser('get')
        self.get_subparsers = get.add_subparsers(title='plugins',
                                                 help='help',
                                                 dest='plugin',
                                                 required=True)
