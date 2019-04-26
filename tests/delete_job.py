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
from hoffclient import Config, Session
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Delete a Hoff job')
    parser.add_argument('--config', '-c', default=None, help='Configuration file')
    parser.add_argument('hoff_job_ids', help='List of Hoff job ids (one or more)', nargs='+')
    args = parser.parse_args()
    conf = Config(args.config)

    with Session(conf) as s:
        jclient = s.jobs
        for job_id in args.hoff_job_ids:
            # delete the job
            jclient.delete(job_id)
