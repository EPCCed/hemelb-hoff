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

import requests
import argparse
import json

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Delete a Hoff job')
    parser.add_argument('conf_file', help='Configuration file')
    parser.add_argument('hoff_job_ids', help='List of Hoff job ids (one or more)', nargs='+')
    args = parser.parse_args()
    conf_file = args.conf_file
    conf = None
    with open(conf_file, 'r') as f:
        conf = json.load(f)

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

        for job_id in args.hoff_job_ids:
        # delete the job
            delete_url = JOBS_URL + "/" + str(job_id)
            p = s.delete(delete_url)
            # check that job was deleted
            assert p.status_code == 200
