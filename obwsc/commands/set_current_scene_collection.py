import argparse

from obwsc.commands.event_based_command import EventBasedCommand

import logging

log = logging.getLogger('obwsc')


class SetCurrentSceneCollection(EventBasedCommand):
    def __init__(self, config, collection: str):
        super().__init__(config)
        self.events.callback.register(self.on_current_scene_collection_changed)
        self.target_collection = collection

    @staticmethod
    def get_parser_name():
        return 'set-current-scene-collection'

    @staticmethod
    def get_help():
        return 'Set the current OBS scene collection'

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument('collection', type=str, help='The name of the OBS scene collection to switch to')

    @staticmethod
    def parse_arguments(args) -> dict:
        return {'collection': args.collection}

    def on_current_scene_collection_changed(self, event):
        if event.scene_collection_name == self.target_collection:
            self.done.set()

    def execute(self):
        scenes = self.ws.get_scene_collection_list()
        if self.target_collection not in scenes.scene_collections:
            raise RuntimeError(f'Scene collection "{self.target_collection}" does not exist')

        if scenes.current_scene_collection_name == self.target_collection:
            log.debug('Scene collection already active')
            return

        self.ws.set_current_scene_collection(self.target_collection)
        self.done.wait()
