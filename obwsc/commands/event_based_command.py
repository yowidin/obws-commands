import obsws_python as obs

import argparse
import logging

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
