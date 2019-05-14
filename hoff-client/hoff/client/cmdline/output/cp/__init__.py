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


def add_verb(parent):
    parser = parent.add_parser("cp", help="copy output of a job to localhost")
    parser.add_argument(
        "--outdir", "-o", default=None, help="Name of directory to fetch results to"
    )
    parser.set_defaults(module=".output.cp.operation", function="run")
    return parser
