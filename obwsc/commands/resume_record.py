from obwsc.commands.event_based_command import EventBasedCommand
from obsws_python.error import OBSSDKRequestError

import sys

from obwsc.log import Log


class ResumeRecord(EventBasedCommand):
    def __init__(self, config):
        super().__init__(config)
        self.events.callback.register(self.on_record_state_changed)

    @staticmethod
    def get_parser_name():
        return 'resume-record'

    @staticmethod
    def get_help():
        return 'Resume a paused OBS recording'

    def on_record_state_changed(self, event):
        if event.output_state == 'OBS_WEBSOCKET_OUTPUT_RESUMED':
            self.done.set()

    def _restart_macos_inputs(self):
        # On macOS the "screen capture" inputs get "broken" after locking the screen, but luckily OBS provides a button
        # for restarting the capture.
        # In this function we are iterating over all inputs, where this button is present and ask OBS to press it.
        if sys.platform != 'darwin':
            Log.debug(f'Skipping screen capture restarts: not on macOS: {sys.platform}')
            return

        resp = self.ws.get_input_list('screen_capture')
        for capture in resp.inputs:
            try:
                self.ws.press_input_properties_button(capture['inputName'], "reactivate_capture")
            except OBSSDKRequestError:
                Log.debug(f'Screen capture reactivation failed for "{capture["inputName"]}"')

    def execute(self):
        status = self.ws.get_record_status()
        if not status.output_active:
            raise RuntimeError('Recording is not active')

        if not status.output_paused:
            Log.debug('Recording is already running')
            self.done.set()
        else:
            self.ws.resume_record()

        self.done.wait()

        self._restart_macos_inputs()
