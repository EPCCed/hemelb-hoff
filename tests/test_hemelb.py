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
import time
from config import MAX_USER_JOBS
import uuid
from tests.test_params import LOGIN_URL, JOBS_URL, INPUTSETS_URL, TEST_TEMPLATE_NAME
from tests.test_params import login_credentials
import os.path

# main set of test functions for the REST interfaces


payload = {}
payload['name'] = "polnet_test"
payload['service'] = "CIRRUS"
#payload['executable'] = "/lustre/home/d411/malcolmi/test_submit/submit.sh"
payload['executable'] = "/lustre/home/shared/d411/hemelb/hoff/templates/master-mouse-bfl-nash-2.sh"
payload['num_total_cpus'] = 2
payload['wallclock_limit'] = 5
payload['project'] = "d411-polnet"
payload['arguments'] = "test.xml"
#payload['filter'] = "results\/.*"
#payload['extended'] = "#PBS -l place=scatter:excl"

#small_files = { 'config.gmy': open('/home/ubuntu/config.gmy','rb'),
#          'test.xml': open('/home/ubuntu/config.xml','rb')
#        }

small_files = { 'config.gmy': open('/home/ubuntu/Myh9KO_ret1_mask_corrected_tubed_smoothed.gmy','rb'),
          'test.xml': open('/home/ubuntu/Myh9KO_ret1_mask_corrected_tubed_smoothed.xml','rb')
        }

big_files = {
    'big_file_1.dat': open('/home/ubuntu/big_file_1.dat','rb'),
    'big_file_2.dat': open('/home/ubuntu/big_file_2.dat','rb'),
    'big_file_3.dat': open('/home/ubuntu/big_file_3.dat','rb')
}


lisa_payload = {}
lisa_payload['name'] = "polnet_test"
lisa_payload['service'] = "LISA"
lisa_payload['executable'] = "/home/millingw/submit.sh"
lisa_payload['num_total_cpus'] = 4
lisa_payload['wallclock_limit'] = 5
#payload['project'] = "d411-polnet"
lisa_payload['arguments'] = "test.xml"
#lisa_payload['filter'] = "results\/.*"
#payload['extended'] = "#PBS -l place=scatter:excl"


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

def testJob():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200

        # An authorised request.
        p = s.post(JOBS_URL, json=payload)
        print p.content
        assert p.status_code == 200
        job_id = p.content
        print job_id

        #upload the small input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.post(file_url, files=small_files)
        assert p.status_code == 200

        # upload the big input files, just to make sure things don't fall over under stress
        #file_url = JOBS_URL + "/" + str(job_id) + "/files"
        #p = s.post(file_url, files=big_files, verify=PEM_CERTIFICATE)
        #assert p.status_code == 200


        #submit the job
        post_url = JOBS_URL + "/" + str(job_id) + "/submit"
        p = s.post(post_url)
        assert p.status_code == 200
        print p.text

        #wait for completion
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url)
        assert p.status_code == 200
        state = p.content

        while state not in ['Done', 'Failed']:
            time.sleep(60)
            p = s.get(get_url)
            assert p.status_code == 200
            state = p.content
            print state

#        assert state == 'Done'

        file_list_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.get(file_list_url)
        assert p.status_code == 200
        file_list = p.json()

        for f in file_list:
            print f


        #print "deleting job"
        #delete_url = JOBS_URL + "/" + str(job_id)
        #p = s.delete(delete_url)
        #assert p.status_code == 200
        #print p.status_code

        #print "checking deleted state"
        #get_url = JOBS_URL + "/" + str(job_id) + "/state"
        #p = s.get(get_url)
        #state = p.content
        #print "final state is " + state
        #assert state == 'DELETED'



def testLisaJob():

    with requests.Session() as s:



        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200

        # An authorised request.
        p = s.post(JOBS_URL, json=lisa_payload)
        print p.content
        assert p.status_code == 200
        job_id = p.content
        print job_id

        #upload the small input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.post(file_url, files=small_files)
        assert p.status_code == 200

        # upload the big input files, just to make sure things don't fall over under stress
#        file_url = JOBS_URL + "/" + str(job_id) + "/files"
#        p = s.post(file_url, files=big_files, verify=PEM_CERTIFICATE)
#        assert p.status_code == 200


        #submit the job
        post_url = JOBS_URL + "/" + str(job_id) + "/submit"
        p = s.post(post_url)
        assert p.status_code == 200
        print p.text

        #wait for completion
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url)
        assert p.status_code == 200
        state = p.content

        while state not in ['Done', 'Failed']:
            time.sleep(60)
            p = s.get(get_url)
            assert p.status_code == 200
            state = p.content
            print state

        assert state == 'Done'

        file_list_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.get(file_list_url)
        assert p.status_code == 200
        file_list = p.json()

        for f in file_list:
            print f


        print "deleting job"
        delete_url = JOBS_URL + "/" + str(job_id)
        p = s.delete(delete_url)
        assert p.status_code == 200
        print p.status_code

        print "checking deleted state"
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url)
        state = p.content
        print "final state is " + state
        assert state == 'DELETED'


# submit a job by specifying a template name rather than providing a job description
def testTemplate():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200

        # try a non-existent template and make sure it behaves itself
        template_payload = {'template_name': "fdsfsdfsdsdfsdfsdfsdfsdfsdfs"}
        p = s.post(JOBS_URL, json=template_payload)
        assert p.status_code == 404

        # now try a real one
        template_payload = {'template_name': TEST_TEMPLATE_NAME, 'arguments': "test.xml" }

        p = s.post(JOBS_URL, json=template_payload)
        print p.content
        assert p.status_code == 200
        job_id = p.content
        print job_id

        #upload the small input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.post(file_url, files=small_files)
        assert p.status_code == 200


        #submit the job
        post_url = JOBS_URL + "/" + str(job_id) + "/submit"
        p = s.post(post_url)
        assert p.status_code == 200
        print p.text

        #wait for completion
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url)
        assert p.status_code == 200
        state = p.content

        while state not in ['Done', 'Failed']:
            time.sleep(60)
            p = s.get(get_url)
            assert p.status_code == 200
            state = p.content
            print state

#        assert state == 'Done'

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

        file_list_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.get(file_list_url)
        assert p.status_code == 200
        file_list = p.json()

        for f in file_list:
            download_file(JOBS_URL, job_id, f, '/home/ubuntu/results', s)

        #print "deleting job"
        #delete_url = JOBS_URL + "/" + str(job_id)
        #p = s.delete(delete_url)
        #assert p.status_code == 200
        #print p.status_code

        #print "checking deleted state"
        #get_url = JOBS_URL + "/" + str(job_id) + "/state"
        #p = s.get(get_url)
        #state = p.content
        #print "final state is " + state
        #assert state == 'DELETED'


# note: this test relies on the user having no active jobs in the test database
# some manual clearup will be needed after running this test
def testJobLimit():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        print p.status_code

        for i in range(0, MAX_USER_JOBS):
            p = s.post(JOBS_URL, json=payload)
            assert p.status_code == 200

        # going one over the limit should fail
        p = s.post(JOBS_URL, json=payload)
        assert p.status_code == 500

        # now get a list of all the jobs, and delete them
        p = s.get(JOBS_URL)
        job_list = p.json()
        for j in job_list:
            job_id = j['local_job_id']
            s.delete(JOBS_URL + "/" +job_id)

        # repeat the test, should be same as before as deleted jobs are not counted
        for i in range(0, MAX_USER_JOBS):
            p = s.post(JOBS_URL, json=payload)
            assert p.status_code == 200

        # going one over the job limit should fail
        p = s.post(JOBS_URL, json=payload)
        assert p.status_code == 500



def testInputSet():

    with requests.Session() as s:
        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200

        name = uuid.uuid4()

        # An authorised request.
        p = s.post(INPUTSETS_URL, data={'name': str(name)})
        assert p.status_code == 200

        id = p.content

        # upload the small input files
        file_url = INPUTSETS_URL + "/" + str(id) + "/files"
        p = s.post(file_url, files=small_files)
        assert p.status_code == 200

        # list the files
        p = s.get(file_url)
        assert p.status_code == 200
        listing = p.json()

        # get the hashcode
        hash_url = INPUTSETS_URL + "/" + str(id) + "/hash"
        p = s.get(file_url)
        assert p.status_code == 200
        hash1 = p.content

        # delete one of the files, then check the hashcode has changed

        delete_url = INPUTSETS_URL + "/" + str(id) + "/files/" + listing[0]
        p = s.delete(delete_url)
        assert p.status_code == 200

        p = s.get(hash_url)
        assert p.status_code == 200
        hash2 = p.content
        assert hash1 != hash2

        # finally delete the inputset.
        # further attempts to retrieve it should fail
        delete_url = INPUTSETS_URL + "/" + str(id)
        p = s.delete(delete_url)
        assert p.status_code == 200
        p = s.get(file_url)
        assert p.status_code == 404




def main():
#    testLisaJob()
    #testJob()
    #testInputSet()
    #testJobLimit()
    testTemplate()



if __name__ == "__main__":
    main()