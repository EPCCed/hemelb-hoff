#!/usr/bin/env python

import os.path
import requests
import os
import argparse
import time
import warnings
import json


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


def submit_and_fetch_simulation(conf, xml_file, gmy_file, template_name, output_dir):
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
        payload = {}
        payload['template_name'] = template_name
        payload['arguments'] = xml_file

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
        parser.add_argument('template_name', help='template name')
        parser.add_argument('conf_file', help='Configuration file')
        args = parser.parse_args()
        xml_file = args.xml_file
        conf_file = args.conf_file
        template_name = args.template_name
        output_dir = os.getcwd()
        gmy_file = get_gmy_filename_from_xml(xml_file)

        conf = None
        with open(conf_file, 'r') as f:
            conf = json.load(f)

        submit_and_fetch_simulation(conf, xml_file, gmy_file, template_name, output_dir)





