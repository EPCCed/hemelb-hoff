#!/usr/bin/env python

"""
   Copyright 2018-2019 EPCC, University Of Edinburgh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os.path
import argparse
import time
import warnings
import xdrlib
import bisect
import sys

from hoff.client import Config, Session
from hoff.client.jobs import JobCreateParams


class Machine:
    SITES_PER_CORE = float(100000)

    @classmethod
    def choose_cores(cls, n_sites):
        ideal_cores = float(n_sites) / cls.SITES_PER_CORE
        ideal_nodes = ideal_cores / cls.CORES_PER_NODE
        # Debugging runs in very small problems
        if ideal_nodes < 0.5:
            return 2
        i = bisect.bisect_left(cls.KNOWN_NODES, ideal_nodes)
        i = min(i, len(cls.KNOWN_NODES) - 1)
        n_nodes = cls.KNOWN_NODES[i]
        n_cores = n_nodes * cls.CORES_PER_NODE
        return n_cores

    @classmethod
    def choose_template(cls, n_sites):
        n_cores = cls.choose_cores(n_sites)
        return cls.TEMPLATE.format(n_cores)


class Cirrus(Machine):
    CORES_PER_NODE = 36
    KNOWN_NODES = [1, 2, 4, 8, 16, 32]
    TEMPLATE = "cirrus_mouse_{}"


def count_sites(gmy_filename):
    with open(gmy_filename, "rb") as gmy:
        preamble = gmy.read(32)
        reader = xdrlib.Unpacker(preamble)
        assert reader.unpack_uint() == 0x686C6221
        assert reader.unpack_uint() == 0x676D7904
        assert reader.unpack_uint() == 4

        block_counts = [reader.unpack_uint() for i in xrange(3)]
        block_size = reader.unpack_uint()
        total_blocks = block_counts[0] * block_counts[1] * block_counts[2]
        header_bytes = total_blocks * 3 * 4
        header = gmy.read(header_bytes)
        pass

    reader = xdrlib.Unpacker(header)

    total_fluid = 0
    for i in range(total_blocks):
        total_fluid += reader.unpack_uint()
        ignored = reader.unpack_uint()
        ignored = reader.unpack_uint()

    return total_fluid


def get_gmy_filename_from_xml(xml_path):
    """Return GMY file as written in XML (i.e. rel to XML)"""
    from xml.etree import ElementTree

    tree = ElementTree.parse(xml_path)
    return tree.getroot().find("geometry/datafile").attrib["path"]


def submit_and_fetch_simulation(conf, xml):
    """Return True on successful execution and fetch results, and False or exception on failure"""
    xml_path_abs = os.path.abspath(xml)
    input_dir = os.path.dirname(xml_path_abs)
    gmy_file_name = os.path.normpath(get_gmy_filename_from_xml(xml_path_abs))
    xml_file_name = os.path.basename(xml_path_abs)
    gmy_path_abs = os.path.normpath(os.path.join(input_dir, gmy_file_name))

    # Copy output files back to the folder where the HemeLB xml config file was
    output_dir = input_dir

    assert gmy_file_name == os.path.basename(gmy_path_abs), "Path issues"
    n_sites = count_sites(gmy_path_abs)
    template_name = Cirrus.choose_template(n_sites)

    POLL_INTERVAL_SECONDS = 15

    def poll(getter, done):
        """Run the nullary function `getter` at least once and then at
        an interval until the unary function `done` returns a true value
        on the result of calling getter. Returns the first value that
        `done` accepts.
        """
        result = getter()
        while not done(result):
            time.sleep(POLL_INTERVAL_SECONDS)
            result = getter()
        return result

    with Session(conf) as s:
        jobclient = s.jobs
        # create a new job using the template name
        jcp = JobCreateParams(template_name=template_name, arguments=xml_file_name)
        # get the job id
        job_id = jobclient.create(jcp)

        # upload the input files
        jobclient.add_input(
            job_id, **{xml_file_name: xml_path_abs, gmy_file_name: gmy_path_abs}
        )

        # submit the job
        jobclient.submit(job_id)

        # wait for completion
        state = poll(
            lambda: jobclient.get_state(job_id),
            lambda state: state in ["Done", "Failed"],
        )

        # job has completed or failed. check to see if the job has been retrieved
        poll(lambda: jobclient.get_retrieved(job_id), lambda ret: ret == 1)

        # get the list of output files
        file_list = jobclient.list_output(job_id)

        # download the files
        jobclient.fetch_output(job_id, file_list)

        # delete the job
        jobclient.delete(job_id)

        return state == "Done"


if __name__ == "__main__":
    with warnings.catch_warnings() as w:
        warnings.simplefilter("ignore")

        parser = argparse.ArgumentParser(description="Submit a HemeLB simulation")
        parser.add_argument("xml_file", help="HemeLB XML input file")
        parser.add_argument("conf_file", help="Configuration file")

        args = parser.parse_args()
        xml_file = args.xml_file
        conf = Config(args.conf_file)

        ok = submit_and_fetch_simulation(conf, xml_file)

        sys.exit(0 if ok else 1)
