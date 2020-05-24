import abc
import logging
import sys


class Cmd(metaclass=abc.ABCMeta):

    description = ''

    def __init__(self):
        self.log = logging.getLogger('plugin')

    def configure_apply(self, parser):
        parser_name = self.__class__.__name__.lower()
        return parser.apply_subparsers.add_parser(parser_name,
                                                  help=self.description)

    def configure_get(self, parser):
        parser_name = self.__class__.__name__.lower()
        return parser.get_subparsers.add_parser(parser_name,
                                                help=self.description)

    def __getattr__(self, item):
        self.log.error('Not implemented')
        sys.exit(1)
