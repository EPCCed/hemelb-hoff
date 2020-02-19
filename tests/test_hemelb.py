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
from tests.test_params import LOGIN_URL, JOBS_URL, INPUTSETS_URL
from tests.test_params import TEST_TEMPLATE_NAME, QUICK_TEMPLATE_NAME, TEST_RESULTS_DIR, QUICK_TEMPLATE_UPLOAD_FILE
from tests.test_params import TEST_UPLOAD_FILE, TEST_CONFIG_FILE, TEST_INPUT_NAME
from tests.test_params import login_credentials
from tests.test_params import login_credentials_user_1, login_credentials_user_2
import os.path

# main set of test functions for the REST interfaces


payload = {}
payload['name'] = "polnet_test"
payload['service'] = "CIRRUS"
payload['executable'] = "/lustre/home/shared/d411/hemelb/hoff/templates/master-mouse-bfl-nash-288.sh"
payload['num_total_cpus'] = 288
payload['wallclock_limit'] = 720
payload['project'] = "d411-polnet"
payload['arguments'] = "config.xml"
payload['filter'] = 'results/.*'


small_files = { 'Myh9KO_ret1_mask_corrected_tubed_smoothed.gmy': open(TEST_UPLOAD_FILE,'rb'),
          'config.xml': open(TEST_CONFIG_FILE,'rb')
        }



sharpen_files = { 'fuzzy.pgm': open(QUICK_TEMPLATE_UPLOAD_FILE,'rb')
        }




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
            print(f)
            download_file(JOBS_URL, job_id, f, TEST_RESULTS_DIR, s)


        #print "deleting job"
        delete_url = JOBS_URL + "/" + str(job_id)
        p = s.delete(delete_url)
        assert p.status_code == 200


        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url)
        state = p.content
        assert state == 'DELETED'






# submit a job by specifying a template name rather than providing a job description
def testTemplate():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200

        template_payload = {'template_name': TEST_TEMPLATE_NAME,
                            'arguments': TEST_INPUT_NAME}

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
            print("Downloading " + f)
            download_file(JOBS_URL, job_id, f, TEST_RESULTS_DIR, s)

        print("deleting job")
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
def testTemplateManyJobs():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200

        template_payload = {'template_name': TEST_TEMPLATE_NAME,
                            'arguments': TEST_INPUT_NAME}

        num_test_jobs = 10
        jobs = []

        for i in range(num_test_jobs):
            p = s.post(JOBS_URL, json=template_payload)
            assert p.status_code == 200
            job_id = p.content
            jobs.append(job_id)

            #upload the small input files
            file_url = JOBS_URL + "/" + str(job_id) + "/files"
            p = s.post(file_url, files= {
                'Myh9KO_ret1_mask_corrected_tubed_smoothed.gmy': open(TEST_UPLOAD_FILE,'rb'),
                TEST_INPUT_NAME: open(TEST_CONFIG_FILE,'rb')} )
            assert p.status_code == 200


            #submit the job
            post_url = JOBS_URL + "/" + str(job_id) + "/submit"
            p = s.post(post_url)
            assert p.status_code == 200
            print p.text


        #wait for completion
        while len(jobs) > 0:
            time.sleep(60)
            print("Polling job state for " + str(len(jobs)) + " jobs")
            for job_id in jobs:
                get_url = JOBS_URL + "/" + str(job_id) + "/state"
                p = s.get(get_url)
                assert p.status_code == 200
                state = p.content
                print(job_id, state)
                if state in ['Done', 'Failed']:
                    get_retrieved_state_url = JOBS_URL + "/" + str(job_id) + "/retrieved"
                    p = s.get(get_retrieved_state_url)
                    assert p.status_code == 200
                    retrieved = int(p.content)
                    if retrieved == 1:
                        file_list_url = JOBS_URL + "/" + str(job_id) + "/files"
                        p = s.get(file_list_url)
                        assert p.status_code == 200
                        file_list = p.json()

                        for f in file_list:
                            print("Downloading " + f)
                            download_file(JOBS_URL, job_id, f, os.path.join(TEST_RESULTS_DIR, job_id), s)

                        print("deleting job")
                        delete_url = JOBS_URL + "/" + str(job_id)
                        p = s.delete(delete_url)
                        assert p.status_code == 200

                        get_url = JOBS_URL + "/" + str(job_id) + "/state"
                        p = s.get(get_url)
                        state = p.content
                        print "final state is " + state
                        assert state == 'DELETED'
                        jobs.remove(job_id)


# submit a job by specifying a template name rather than providing a job description
def testQuickTemplate():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=login_credentials)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert p.status_code == 200


        # now try a real one
        template_payload = {'template_name': QUICK_TEMPLATE_NAME }

        p = s.post(JOBS_URL, json=template_payload)
        print p.content
        assert p.status_code == 200
        job_id = p.content
        print job_id

        #upload the small input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.post(file_url, files=sharpen_files)
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
            print(f)
            download_file(JOBS_URL, job_id, f, TEST_RESULTS_DIR, s)

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



# test jobs from different users at the same time
def testQuickMultiUser():

    session_a = requests.Session()
    p1 = session_a.post(LOGIN_URL, data=login_credentials_user_1)
    # print the html returned or something more intelligent to see if it's a successful login page.
    assert p1.status_code == 200

    session_b = requests.Session()
    p2 = session_b.post(LOGIN_URL, data=login_credentials_user_2)
    # print the html returned or something more intelligent to see if it's a successful login page.
    assert p2.status_code == 200


    p1 = session_a.post(JOBS_URL, json={'template_name': QUICK_TEMPLATE_NAME})
    assert p1.status_code == 200
    job_id_a = p1.content

    p2 = session_b.post(JOBS_URL, json={'template_name': QUICK_TEMPLATE_NAME})
    assert p2.status_code == 200
    job_id_b = p2.content

    p1 = session_a.post(JOBS_URL + "/" + str(job_id_a) + '/files', files={'fuzzy.pgm': open(QUICK_TEMPLATE_UPLOAD_FILE,'rb')})
    assert p1.status_code == 200

    p2 = session_b.post(JOBS_URL + "/" + str(job_id_b) + '/files', files={'fuzzy.pgm': open(QUICK_TEMPLATE_UPLOAD_FILE, 'rb')})
    assert p2.status_code == 200

    p1 = session_a.post(JOBS_URL + '/' + str(job_id_a) + '/submit')
    assert p1.status_code == 200

    p2 = session_b.post(JOBS_URL + '/' + str(job_id_b) + '/submit')
    assert p2.status_code == 200

    p1 = session_a.get(JOBS_URL + '/' + str(job_id_a) + '/state')
    state_a = p1.content
    p2 = session_b.get(JOBS_URL + '/' + str(job_id_b) + '/state')
    state_b = p2.content

    while (state_a not in ['Done', 'Failed']) and (state_b not in ['Done', 'Failed']):
        p1 = session_a.get(JOBS_URL + '/' + str(job_id_a) + '/state')
        state_a = p1.content
        p2 = session_b.get(JOBS_URL + '/' + str(job_id_b) + '/state')
        state_b = p2.content

        print state_a, state_b

        time.sleep(60)

    p1 = session_a.delete(JOBS_URL + '/' + str(job_id_a))
    assert p1.status_code == 200
    p2 = session_b.delete(JOBS_URL + '/' + str(job_id_b))
    assert p2.status_code == 200





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



# make sure that users with different accounts can't interfere with each other's jobs
def testMultipleUsers():

    template_payload = {'template_name': TEST_TEMPLATE_NAME,
                            'arguments': TEST_INPUT_NAME}

    user_session_a = requests.session()
    p1 = user_session_a.post(LOGIN_URL, data=login_credentials_user_1)
    assert p1.status_code == 200

    p1 = user_session_a.post(JOBS_URL, json=template_payload)
    assert p1.status_code == 200
    job_id_a = p1.content

    user_session_b = requests.session()
    p2 = user_session_b.post(LOGIN_URL, data=login_credentials_user_2)
    assert p2.status_code == 200

    p2 = user_session_b.post(JOBS_URL, json=template_payload)
    assert p2.status_code == 200
    job_id_b = p2.content

    # check the users can't see each other's jobs
    job_listing_a = user_session_a.get(JOBS_URL).json()
    job_listing_b = user_session_b.get(JOBS_URL).json()

    found_job = False
    for j in job_listing_a:
        assert(j['local_job_id'] != job_id_b)
        if j['local_job_id'] == job_id_a:
            found_job = True
    assert(found_job)

    found_job = False
    for j in job_listing_b:
        assert (j['local_job_id'] != job_id_a)
        if j['local_job_id'] == job_id_b:
            found_job = True
    assert (found_job)

    # check the users can't submit each others jobs
    p1 = user_session_a.post(JOBS_URL + '/' + job_id_b + '/' + 'submit')
    assert (p1.status_code == 403)
    p2 = user_session_b.post(JOBS_URL + '/' + job_id_a + '/' + 'submit')
    assert (p2.status_code == 403)

    # TODO - check the users can't modify or list each other's files
    p1 = user_session_a.get(JOBS_URL + '/' + job_id_b + '/files')
    assert (p1.status_code == 403)
    p2 = user_session_b.get(JOBS_URL + '/' + job_id_a + '/files')
    assert (p2.status_code == 403)

    # check the users can't delete each other's jobs
    print job_id_a, job_id_b
    p2 = user_session_b.delete(JOBS_URL + '/' + job_id_a)
    assert (p2.status_code == 403)
    p1 = user_session_a.delete(JOBS_URL + '/' + job_id_b)
    assert(p1.status_code == 403)


    # cleanup, shouldn't be any issues
    p1 = user_session_a.delete(JOBS_URL + '/' + job_id_a)
    assert (p1.status_code == 200)
    p2 = user_session_b.delete(JOBS_URL + '/' + job_id_b)
    assert (p2.status_code == 200)



def main():
#    testLisaJob()
    #testJob()
    #testInputSet()
    #testJobLimit()
    #testTemplateManyJobs()
    testQuickTemplate()
    testMultipleUsers()
    testQuickMultiUser()



if __name__ == "__main__":
    main()