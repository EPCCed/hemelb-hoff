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

from setuptools import setup

setup(
    name="hoff-client",
    version="0.1.0",
    author="Rupert Nash",
    author_email="r.nash@epcc.ed.ac.uk",
    description="HemeLB offload client",
    namespace_packages=["hoff"],
    packages=[
        "hoff",
        "hoff.client",
        "hoff.client.cmdline",
        "hoff.client.cmdline.job",
        "hoff.client.cmdline.job.ls",
        "hoff.client.cmdline.job.rm",
        "hoff.client.cmdline.output",
        "hoff.client.cmdline.output.cp",
        "hoff.client.cmdline.output.ls",
    ],
    install_requires=["requests"],
    entry_points={
        "console_scripts": ["hoff = hoff.client.cmdline:main"]
    },
)
