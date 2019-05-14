# Copyright 2018-2019 EPCC, University Of Edinburgh

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
