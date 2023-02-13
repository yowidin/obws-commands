from obwsc.commands.event_based_command import EventBasedCommand

import logging

log = logging.getLogger('obwsc')


class StartRecord(EventBasedCommand):
    def __init__(self, config):
        super().__init__(config)
        self.events.callback.register(self.on_record_state_changed)

    @staticmethod
    def get_parser_name():
        return 'start-record'

    @staticmethod
    def get_help():
        return 'Start an OBS recording'

    def on_record_state_changed(self, event):
        if event.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED':
            self.done.set()

    def execute(self):
        status = self.ws.get_record_status()
        if status.output_active:
            log.debug('Recording is already running')
            self.done.set()
            return

        self.ws.start_record()
        self.done.wait()

