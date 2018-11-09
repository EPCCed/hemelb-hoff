import requests
import time
from config import MAX_USER_JOBS

#BASE_URL = "http://127.0.0.1:5000"

BASE_URL = "https://129.215.193.177"

LOGIN_URL = BASE_URL + "/admin/login/"
JOBS_URL = BASE_URL + "/jobs"
INPUTSETS_URL = BASE_URL + "/inputsets"


params = {
    'email': "admin",
    'password': "Ukprd128!!!"
}

payload = {}
payload['name'] = "polnet_test"
payload['service'] = "CIRRUS"
payload['executable'] = "/lustre/home/d411/malcolmi/test_submit/submit.sh"
payload['num_total_cpus'] = 36
payload['wallclock_limit'] = 5
payload['project'] = "d411-polnet"
payload['arguments'] = "david, hassell, hoff"

small_files = { 'config.gmy': open('/home/ubuntu/config.gmy','rb'),
          'config.xml': open('/home/ubuntu/config.xml','rb')
        }


def testJob():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=params, verify = False)
        # print the html returned or something more intelligent to see if it's a successful login page.
        print p.status_code

        # An authorised request.
        p = s.post(JOBS_URL, json=payload, verify = False)
        job_id = p.content
        print job_id

        #upload the small input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        p = s.post(file_url, files=small_files, verify = False)
        print p.status_code


        #submit the job
        post_url = JOBS_URL + "/" + str(job_id) + "/submit"
        p = s.post(post_url, verify = False)
        print p.text

        #wait for completion
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url, verify = False)
        state = p.content

        while state not in ['Done', 'Failed']:
            time.sleep(60)
            p = s.get(get_url, verify = False)
            state = p.content
            print state

        print "deleting job"
        delete_url = JOBS_URL + "/" + str(job_id)
        p = s.delete(delete_url, verify = False)
        print p.status_code

        print "checking deleted state"
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url, verify = False)
        state = p.content
        print "final state is " + state


# note: this test relies on the user having no active jobs in the test database
# some manual clearup will be needed after running this test
def testJobLimit():

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=params)
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
        p = s.post(LOGIN_URL, data=params)
        # print the html returned or something more intelligent to see if it's a successful login page.
        print p.status_code

        # An authorised request.
        p = s.post(INPUTSETS_URL, data={'name': 'myname2'})
        id = p.content
        print id

        # upload the small input files
        file_url = INPUTSETS_URL + "/" + str(id) + "/files"
        p = s.post(file_url, files=small_files)
        print p.status_code

        # list the files
        p = s.get(file_url)
        print p.content


def main():
    testJob()



if __name__ == "__main__":
    main()