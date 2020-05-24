import json
import logging
import pkg_resources
import sys

from dashdotdb.cli.parser import Parser


APP_LOG = logging.getLogger('app')
APP_LOG_HANDLER = logging.StreamHandler(sys.stdout)
APP_LOG_HANDLER.setFormatter(logging.Formatter(fmt='%(message)s'))
APP_LOG.addHandler(APP_LOG_HANDLER)
APP_LOG.setLevel(logging.INFO)

PLUGIN_LOG = logging.getLogger('plugin')
PLUGIN_LOG_HANDLER = logging.StreamHandler(sys.stdout)
PLUGIN_LOG_HANDLER.setFormatter(logging.Formatter(fmt='%(message)s'))
PLUGIN_LOG.addHandler(PLUGIN_LOG_HANDLER)
PLUGIN_LOG.setLevel(logging.INFO)

class DashDotDB:
    def __init__(self):
        self.parser = Parser()

    def run(self):
        plugins = dict()
        for entry_point in pkg_resources.iter_entry_points('plugins'):
            mod = entry_point.load()
            plugins[entry_point.name] = mod()

            for choice in self.parser.actions.choices:
                # The configure_* methods are the interface for the plugins to
                # extend the action (apply, get, ...) command line arguments
                configure_func = getattr(plugins[entry_point.name], f'configure_{choice}')
                configure_func(self.parser)

        args, _ = self.parser.application.parse_known_args()
        # We execute the "action" (apply, get, ...) method of the
        # selected plugin
        action_func = getattr(plugins[args.plugin], args.action, None)
        if action_func is None:
            APP_LOG.error('Not implemented')
            sys.exit(1)
        action_func(args)


def main():
    cli = DashDotDB()
    cli.run()
