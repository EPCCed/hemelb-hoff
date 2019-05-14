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
from . import ls
from . import cp


def add_subcommand(parent):
    parser = parent.add_parser("output", help="output related commands")
    parser.add_argument("job_id", help="Hoff job ID")
    verbs = parser.add_subparsers(help="output action help")
    ls.add_verb(verbs)
    cp.add_verb(verbs)
