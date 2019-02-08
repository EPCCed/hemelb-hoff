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
import requests
import os
import argparse
import time
import warnings
import json


class Machine:
    SITES_PER_CORE = float(100000)
    @classmethod
    def choose_cores(cls, n_sites):
        ideal_cores = float(n_sites) / cls.SITES_PER_CORE
        ideal_nodes = ideal_cores / cls.CORES_PER_NODE
        i = bisect.bisect_left(cls.KNOWN_NODES, ideal_nodes)
        i = min(i, len(cls.KNOWN_NODES) - 1)
        n_nodes = cls.KNOWN_NODES[i]
        n_cores = n_nodes * cls.CORES_PER_NODE
        
    @classmethod
    def choose_template(cls, n_sites):
        n_cores = cls.choose_cores(n_sites)
        return cls.TEMPLATE.format(n_cores)

class Cirrus(Machine):
    CORES_PER_NODE = 36
    KNOWN_NODES = [1, 2, 4, 8, 16]
    TEMPLATE = 'cirrus_mouse_{}'


def count_sites(gmy_filename):
    with open(gmy_filename, 'rb') as gmy:
        preamble = gmy.read(32)
        reader = xdrlib.Unpacker(preamble)
        assert(reader.unpack_uint() == 0x686c6221)
        assert(reader.unpack_uint() == 0x676d7904)
        assert(reader.unpack_uint() == 4)

        block_counts = [read.unpack_uint() for i in xrange(3)]
        block_size = read.unpack_uint()
        total_blocks = block_counts[0]*block_counts[1]*block_counts[2]
        header_bytes =  total_blocks * 3 * 4
        header = gmy.read(header_bytes)
        pass

    reader = xdrlib.Unpacker(header)

    total_fluid = 0
    for i in range(total_blocks):
        total_fluid += reader.unpack_uint()
        ignored = reader.unpack_uint()
        ignored = reader.unpack_uint()

    return total_fluid

def get_gmy_filename_from_xml(xml_filename):
    from xml.etree import ElementTree
    tree = ElementTree.parse(xml_filename)
    gmy_filename = tree.getroot().find('geometry/datafile').attrib['path']
    return gmy_filename


def download_file(JOBS_URL, job_id, filename, output_dir, session):
    file_url = JOBS_URL + "/" + job_id + "/files/" + filename
    local_filename = os.path.join(output_dir, filename)

    if not os.path.exists(os.path.dirname(local_filename)):
        os.makedirs(os.path.dirname(local_filename))

    r = session.get(file_url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def submit_and_fetch_simulation(conf, xml_file, gmy_file, output_dir):
    with requests.Session() as s:


        login_credentials = {
            'email': conf['username'],
            'password': conf['password']
        }

        BASE_URL = conf['server_url']
        LOGIN_URL = BASE_URL + "/admin/login/"
        JOBS_URL = BASE_URL + "/jobs"

        # log into the Hoff
        p = s.post(LOGIN_URL, data=login_credentials)
        # check we logged in ok
        assert p.status_code == 200

        # create a new job using the template name
        n_sites = count_sites(gmy_file)
        template_name = Cirrus.choose_template(n_sites)
        args = '{} {}'.format(Cirrus.choose_cores(n_sites), xml_file)
        payload = {}
        payload['template_name'] = template_name
        payload['arguments'] = args

        # Post the job spec, job is created with NEW state
        p = s.post(JOBS_URL, json=payload)
        assert p.status_code == 200

        # get the job id from the response
        job_id = p.content

        # upload the input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        input_files = {xml_file: open(xml_file, 'rb'), gmy_file: open(gmy_file, 'rb')}
        p = s.post(file_url, files=input_files)
        assert p.status_code == 200

        # submit the job
        post_url = JOBS_URL + "/" + str(job_id) + "/submit"
        p = s.post(post_url)
        assert p.status_code == 200

        # wait for completion
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url)
        assert p.status_code == 200
        state = p.content

        while state not in ['Done', 'Failed']:
            time.sleep(30)
            p = s.get(get_url)
            assert p.status_code == 200
            state = p.content

        assert state == 'Done'

        # job has completed or failed. check to see if the job has been retrieved
        get_retrieved_state_url = JOBS_URL + "/" + str(job_id) + "/retrieved"
        p = s.get(get_retrieved_state_url)
        assert p.status_code == 200
        retrieved = int(p.content)

        while retrieved != 1:
            time.sleep(30)
            p = s.get(get_retrieved_state_url)
            assert p.status_code == 200
            retrieved = int(p.content)

        # get the list of output files
        file_list_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.get(file_list_url)
        assert p.status_code == 200
        file_list = p.json()

        # download the files
        for f in file_list:
            download_file(JOBS_URL, job_id, f, output_dir, s)

        # delete the job
        delete_url = JOBS_URL + "/" + str(job_id)
        p = s.delete(delete_url)
        assert p.status_code == 200


if __name__ == '__main__':
    with warnings.catch_warnings() as w:
        warnings.simplefilter("ignore")
        parser = argparse.ArgumentParser(description='Submit a HemeLB simulation')
        parser.add_argument('xml_file', help='HemeLB XML input file')
        #parser.add_argument('template_name', help='template name')
        parser.add_argument('conf_file', help='Configuration file')
        args = parser.parse_args()
        xml_file = args.xml_file
        conf_file = args.conf_file
        #template_name = None if args.template_name.lower() == 'none' else args.template_name
        output_dir = os.getcwd()
        gmy_file = get_gmy_filename_from_xml(xml_file)

        conf = None
        with open(conf_file, 'r') as f:
            conf = json.load(f)

        submit_and_fetch_simulation(conf, xml_file, gmy_file, output_dir)

