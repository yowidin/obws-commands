from argparse import ArgumentParser

import logging


class Log:
    @staticmethod
    def add_args(parser: ArgumentParser):
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument('-v', dest='info', action='store_true', help='Log info messages')
        verbosity.add_argument('-vv', dest='debug', action='store_true', help='Log debug messages')

    @staticmethod
    def setup(args):
        if args.info:
            level = logging.INFO
        elif args.debug:
            level = logging.DEBUG
        else:
            level = logging.ERROR

        logging.basicConfig(level=level)
