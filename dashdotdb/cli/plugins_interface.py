import abc
import logging


class Cmd(metaclass=abc.ABCMeta):

    description = ''

    def __init__(self):
        self.log = logging.getLogger('app')

    def configure_apply(self, parser):
        return parser.apply_subparsers.add_parser(self.__class__.__name__.lower(),
                                                  help=self.description)

    def configure_get(self, parser):
        return parser.get_subparsers.add_parser(self.__class__.__name__.lower(),
                                                help=self.description)

    @abc.abstractmethod
    def apply(self, args):
        """
        :param args:
        :return:
        """

    @abc.abstractmethod
    def get(self, args):
        """
        :param args:
        :return:
        """
