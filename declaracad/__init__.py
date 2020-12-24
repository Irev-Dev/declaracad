"""
Copyright (c) 2017-2020, Jairus Martin.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Dec 6, 2015

@author: jrm
"""
import os
import sys
import logging
import faulthandler
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler


version = '0.4.0dev'

LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(name)s | %(message)s'


def get_log_dir():
    log_dir = os.path.expanduser('~/.config/declaracad/logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def get_log_filename():
    log_dir = get_log_dir()
    return os.path.join(log_dir, 'declaracad.txt')


def init_logging(log_format=LOG_FORMAT):
    """ Log to stdout and the file """

    log_filename = get_log_filename()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)

    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    stream.setFormatter(formatter)

    #: Log to rotating handler
    disk = RotatingFileHandler(
        log_filename,
        maxBytes=1024*1024*10,  # 10 MB
        backupCount=10,
    )
    disk.setLevel(logging.DEBUG)
    disk.setFormatter(formatter)

    log.addHandler(disk)
    log.addHandler(stream)

    #: Set ipython logging to warning
    for name in ('ipykernel.inprocess.ipkernel', 'traitlets',
                 'parso.python.diff', 'parso.cache'):
        log = logging.getLogger(name)
        log.setLevel(logging.WARNING)

    # Needs to be here to make windows happy
    faulthandler.enable()


def launch_exporter(args):
    init_logging()
    from declaracad.apps import exporter
    exporter.main(**args.__dict__)


def launch_viewer(args):
    if args.frameless:
        init_logging('%(message)s')
    else:
        init_logging()
    from declaracad.apps import viewer
    viewer.main(**args.__dict__)


def launch_workbench(args):
    init_logging()
    from declaracad.apps import workbench
    workbench.main(**args.__dict__)


def main():
    is_frozen = getattr(sys, "frozen", False)

    if is_frozen and sys.platform == 'win32':
        # Redirect stderr and stdout to a file on windows
        # log_dir = get_log_dir()
        # sys.stdout = open(os.path.join(log_dir, 'io.txt'), 'a')
        # sys.stderr = open(os.path.join(log_dir, 'stderr.txt'), 'a')
        pass  # Doesn't work

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='DeclaraCAD subcommands')
    viewer = subparsers.add_parser("view", help="View the given file")
    viewer.set_defaults(func=launch_viewer)
    viewer.add_argument("file", help="File to view")
    viewer.add_argument("-w", "--watch", action='store_true',
                        help="Watch for file changes and autoreload")
    viewer.add_argument("-f", "--frameless", action='store_true',
                        help="Frameless viewer")

    exporter = subparsers.add_parser("export", help="Export the given file")
    exporter.set_defaults(func=launch_exporter)
    exporter.add_argument("options", help="File to export or json string of "
                                          "ExportOption parameters")
    args = parser.parse_args()

    # Start the app
    launcher = getattr(args, 'func', launch_workbench)
    launcher(args)


if __name__ == '__main__':
    main()
