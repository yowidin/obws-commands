import obsws_python as obs

import argparse
import logging
import time

from threading import Event

log = logging.getLogger('obwsc')


class EventBasedCommand:
    """
    Base class for commands that have the following workflow:
    1. Send a request to OBS
    2. Wait for a specific event from OBS
    3. Complete
    """

    def __init__(self, config):
        self.ws = obs.ReqClient(**config)
        self.events = obs.EventClient(**config)
        self.events.callback.register(self.on_exit_started)
        self.done = Event()

    def on_exit_started(self, _):
        self.events.unsubscribe()
        log.warning('OBS is shutting down')
        self.done.set()

    def execute(self):
        raise NotImplementedError()

    @staticmethod
    def get_parser_name():
        return None

    @staticmethod
    def get_help():
        return None

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def parse_arguments(_) -> dict:
        return {}

    def __enter__(self):
        self.ws.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Events listener has a stupid thread loop in it, and may not be closed before we exit the context
        # it also doesn't have any sort of error handling, so it will most likely output exceptions upon shutdown -_-
        # This should be fixed in the library, and then removed here.
        time.sleep(self.events.DELAY * 2)
        self.events.unsubscribe()
        time.sleep(self.events.DELAY * 2)

        self.ws.__exit__(exc_type, exc_val, exc_tb)
