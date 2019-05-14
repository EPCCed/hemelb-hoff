from __future__ import absolute_import
import argparse
import importlib
from . import job
from . import output


def run(args):
    mod = importlib.import_module(args.module, package="hoff.client.cmdline")
    f = getattr(mod, args.function)
    return f(args)


def make_parser():
    hoff = argparse.ArgumentParser(
        prog="hoff", description="Hoff client command line help"
    )
    hoff.add_argument("--config", "-c", default=None, help="Configuration file")

    sub_cmds = hoff.add_subparsers(help="sub-command help")
    job.add_subcommand(sub_cmds)
    output.add_subcommand(sub_cmds)
    return hoff


def main():
    p = make_parser()
    args = p.parse_args()
    run(args)
