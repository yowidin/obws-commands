from argparse import ArgumentParser
from typing import Callable, Optional

import os
import sys

import toml

from obwsc.log import Log


class Options:
    @staticmethod
    def _get_default_working_dir() -> str:
        result = os.path.dirname(sys.argv[0])

        # Handle the case where we are compiled into a standalone package
        if sys.platform == 'darwin' and 'Contents/MacOS' in result:
            # We are inside an macOS bundle
            result = os.path.abspath(os.path.join(result, '..', '..', '..'))
        else:
            result = os.getcwd()

        return result

    @staticmethod
    def parse(name: str, extra_args_fn: Optional[Callable[[ArgumentParser], None]] = None):
        parser = ArgumentParser(name)

        Log.add_args(parser)

        parser.add_argument('--config', '-c',
                            default=os.path.join(Options._get_default_working_dir(), 'config.toml'),
                            required=False, help='Path to the TOML configuration file')
        parser.add_argument('--host', '-a', default=None, type=str, required=False,
                            help='Host address, the OBS WS is running on')
        parser.add_argument('--port', '-p', default=None, type=int, required=False,
                            help='Port number, the OBS WS is running on')
        parser.add_argument('--password', '-s', default=None, type=str, required=False, help='OBS Web Socket Password')

        if extra_args_fn is not None:
            extra_args_fn(parser)

        args = parser.parse_args()

        Log.setup(args)

        if os.path.exists(args.config) and os.path.isfile(args.config):
            config = toml.load(args.config)
        else:
            config = {'obs': {'host': None, 'port': None, 'password': None}}

        def set_if_present(key: str, value):
            if value is not None:
                config['obs'][key] = value

        set_if_present('host', args.host)
        set_if_present('port', args.port)
        set_if_present('password', args.password)

        if config['obs']['host'] is None or config['obs']['port'] is None:
            raise RuntimeError(
                'Host and port values are required (either via config.toml or as command line arguments)')

        return config, args
