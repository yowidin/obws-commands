#!/usr/bin/env python3
import inspect
import pkgutil
import sys
import argparse

from obsws_python.error import OBSSDKError

from obwsc.options import Options
from obwsc.commands.event_based_command import EventBasedCommand

import obwsc.commands

from typing import Optional


def get_classes(package):
    imported = {}
    prefix = package.__name__ + "."
    for importer, modname, is_package in pkgutil.iter_modules(package.__path__, prefix):
        if is_package:
            continue

        imported[modname] = __import__(modname, fromlist='main')

    return imported


def collect_commands_from_modules(modules):
    res = set()
    for key in modules:
        module = modules[key]
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue

            if name == 'EventBasedCommand':
                continue

            if issubclass(obj, EventBasedCommand):
                res.add(obj)

    return [x for x in res]


def collect_commands():
    # noinspection PyTypeChecker
    return collect_commands_from_modules(get_classes(package=obwsc.commands))


def main():
    commands = collect_commands()
    parsers = {}
    arg_parser = None  # type: Optional[argparse.ArgumentParser]

    def add_command_parsers(parser):
        nonlocal arg_parser, parsers
        arg_parser = parser

        subparsers = parser.add_subparsers(title='command', dest='command', help='Command to execute')
        for cmd in commands:
            name = cmd.get_parser_name()
            hlp = cmd.get_help()
            if name is None or hlp is None:
                continue

            if name in parsers:
                raise RuntimeError(f'Duplicate command name: {name}, already used by "{parsers[name]}"')

            parsers[name] = cmd
            command_parser = subparsers.add_parser(name, help=hlp)
            cmd.add_arguments(command_parser)

    config, args = Options.parse('obws-command', extra_args_fn=add_command_parsers)

    if args.command is None:
        arg_parser.print_usage(sys.stderr)
        raise RuntimeError('Missing required argument: command')

    obs_config = config['obs']

    command = parsers[args.command]
    extra_args = command.parse_arguments(args)
    result = command(obs_config, **extra_args).execute()
    if result is not None:
        print(result)


def run():
    try:
        main()
        sys.exit(0)
    except OBSSDKError as e:
        print(e)
    except ConnectionRefusedError as e:
        print(f'Connection refused, please make sure OBS is running', file=sys.stderr)
    except RuntimeError as e:
        print(e, file=sys.stderr)

    sys.exit(-1)


if __name__ == '__main__':
    run()
