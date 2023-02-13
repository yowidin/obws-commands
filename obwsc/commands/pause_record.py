from obwsc.commands.event_based_command import EventBasedCommand

import logging

log = logging.getLogger('obwsc')


class PauseRecord(EventBasedCommand):
    def __init__(self, config):
        super().__init__(config)
        self.events.callback.register(self.on_record_state_changed)

    @staticmethod
    def get_parser_name():
        return 'pause-record'

    @staticmethod
    def get_help():
        return 'Pause an active OBS recording'

    def on_record_state_changed(self, event):
        if event.output_state == 'OBS_WEBSOCKET_OUTPUT_PAUSED':
            self.done.set()

    def execute(self):
        status = self.ws.get_record_status()
        if not status.output_active:
            raise RuntimeError('Recording is not active')

        if status.output_paused:
            log.debug('Recording is already paused')
            self.done.set()
            return

        self.ws.pause_record()
        self.done.wait()

