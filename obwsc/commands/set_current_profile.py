import argparse

from obwsc.commands.event_based_command import EventBasedCommand

import logging

log = logging.getLogger('obwsc')


class SetCurrentProfile(EventBasedCommand):
    def __init__(self, config, profile: str):
        super().__init__(config)
        self.events.callback.register(self.on_current_profile_changed)
        self.target_profile = profile

    @staticmethod
    def get_parser_name():
        return 'set-current-profile'

    @staticmethod
    def get_help():
        return 'Set the current OBS profile. This can only be done when no recording is active.'

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument('profile', type=str, help='The name of the OBS profile to switch to')

    @staticmethod
    def parse_arguments(args) -> dict:
        return {'profile': args.profile}

    def on_current_profile_changed(self, event):
        if event.profile_name == self.target_profile:
            self.done.set()

    def execute(self):
        profiles = self.ws.get_profile_list()
        if self.target_profile not in profiles.profiles:
            raise RuntimeError(f'Profile "{self.target_profile}" does not exist')

        if profiles.current_profile_name == self.target_profile:
            log.debug('Profile already active')
            return

        status = self.ws.get_record_status()
        if status.output_active:
            raise RuntimeError('Profile cannot be changed while recording is active')

        self.ws.set_current_profile(self.target_profile)
        self.done.wait()

