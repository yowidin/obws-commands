from argparse import ArgumentParser

import logging
from typing import Optional


class Log:
    INSTANCE = None  # type: Optional[Log]
    LOGGER_NAME = 'obwsc'
    FORMAT_STRING = '[%(asctime)s][%(levelname)s][%(name)s] %(message)s'

    def __init__(self, level: int):
        self.formatter = logging.Formatter(Log.FORMAT_STRING)
        self.level = level

        self.logger = logging.getLogger(Log.LOGGER_NAME)
        self.logger.setLevel(level)
        self.logger.propagate = False

        self.handlers = []
        self._add_handler(self.logger, logging.StreamHandler())

    def _add_handler(self, logger, handler):
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        logger.addHandler(handler)
        self.handlers.append(handler)

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

        if Log.INSTANCE is None:
            Log.INSTANCE = Log(level)

    def update_level(self, level):
        self.logger.setLevel(level)
        for handler in self.handlers:
            handler.setLevel(level)

    @staticmethod
    def debug(*args, **kwargs):
        assert Log.INSTANCE is not None
        Log.INSTANCE.logger.debug(*args, **kwargs)

    @staticmethod
    def info(*args, **kwargs):
        assert Log.INSTANCE is not None
        Log.INSTANCE.logger.info(*args, **kwargs)

    @staticmethod
    def warning(*args, **kwargs):
        assert Log.INSTANCE is not None
        Log.INSTANCE.logger.warning(*args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        assert Log.INSTANCE is not None
        Log.INSTANCE.logger.error(*args, **kwargs)

    @staticmethod
    def exception(*args, **kwargs):
        assert Log.INSTANCE is not None
        Log.INSTANCE.logger.exception(*args, **kwargs)

    @staticmethod
    def fatal(*args, **kwargs):
        assert Log.INSTANCE is not None
        Log.INSTANCE.logger.fatal(*args, **kwargs)