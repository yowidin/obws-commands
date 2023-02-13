import argparse
import time

from obwsc.commands.event_based_command import EventBasedCommand
from obwsc.commands.stop_record import StopRecord
from obwsc.commands.start_record import StartRecord
from obwsc.commands.set_current_profile import SetCurrentProfile
from obwsc.commands.set_current_scene_collection import SetCurrentSceneCollection

import logging

log = logging.getLogger('obwsc')


class SwitchProfileAndSceneCollection(EventBasedCommand):
    def __init__(self, config, profile: str, collection: str):
        super().__init__(config)
        self.config = config
        self.target_profile = profile
        self.target_collection = collection

    @staticmethod
    def get_parser_name():
        return 'switch-profile-and-scene-collection'

    @staticmethod
    def get_help():
        return 'Switch the current OBS profile and scene collection, stopping the recording if necessary'

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument('profile', type=str, help='The name of the OBS profile to switch to')
        parser.add_argument('scene', type=str, help='The name of the OBS scene collection to switch to')

    @staticmethod
    def parse_arguments(args) -> dict:
        return {'profile': args.profile, 'collection': args.scene}

    def execute(self):
        profiles = self.ws.get_profile_list()
        if self.target_profile not in profiles.profiles:
            raise RuntimeError(f'Profile "{self.target_profile}" does not exist')

        change_profile = profiles.current_profile_name != self.target_profile

        scenes = self.ws.get_scene_collection_list()
        if self.target_collection not in scenes.scene_collections:
            raise RuntimeError(f'Scene collection "{self.target_collection}" does not exist')

        change_scene = scenes.current_scene_collection_name != self.target_collection

        if not change_profile and not change_scene:
            log.debug('Profile and scene collection already active')
            return

        if change_profile:
            StopRecord(self.config).execute()
            time.sleep(1)  # OBS Reports an old status even after generating a "recording stopped" event
            SetCurrentProfile(self.config, self.target_profile).execute()

        if change_scene:
            SetCurrentSceneCollection(self.config, self.target_collection).execute()

        StartRecord(self.config).execute()
