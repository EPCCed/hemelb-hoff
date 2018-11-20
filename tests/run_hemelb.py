import requests
import time
import os

#BASE_URL = "https://129.215.193.177"
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = BASE_URL + "/admin/login/"
JOBS_URL = BASE_URL + "/jobs"
INPUTSETS_URL = BASE_URL + "/inputsets"
PEM_CERTIFICATE = "/home/ubuntu/hoff-server.pem"
JOB_STATE_REFRESH_PERIOD = 60
LOCAL_FILE_DIR = "/home/ubuntu/testdir"



#login_credentials = {
#    'email': "admin",
#    'password': "hibernian-hibernian"
#}

login_credentials = {
    'email': "admin",
    'password': "admin"
}

#note: if specified, filer must be a valid python regular expression

job_spec = {
'name': 'polnet_test',
'service': 'CIRRUS',
'executable': '/lustre/home/d411/malcolmi/test_submit/submit.sh',
'num_total_cpus': 36,
'wallclock_limit': 5,
'project': 'd411-polnet',
'arguments': 'david, hassel, hoff',
'filter': ".+\.dat"
}

input_files = { 'config.gmy': open('/home/ubuntu/config.gmy','rb'),
          'config.xml': open('/home/ubuntu/config.xml','rb')
        }


def download_file(job_id, filename, session):
    file_url = JOBS_URL + "/" + job_id + "/files" + filename
    local_filename = os.path.join(LOCAL_FILE_DIR, job_id, filename)

    if not os.path.exists(os.path.dirname(local_filename)):
        os.makedirs(os.path.dirname(local_filename))

    r = session.get(file_url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)


def runJob():

    with requests.Session() as s:

        # log into the Hoff
        p = s.post(LOGIN_URL, data=login_credentials, verify = PEM_CERTIFICATE)
        # check we logged in ok
        assert p.status_code == 200

        # Post the job spec, job is created with NEW state
        p = s.post(JOBS_URL, json=job_spec, verify = PEM_CERTIFICATE)
        assert p.status_code == 200

        # get the job id from the response
        job_id = p.content
        print job_id

        #upload the input files
        file_url = JOBS_URL + "/" + str(job_id) + "/files"
        print file_url
        p = s.post(file_url, files=input_files, verify = PEM_CERTIFICATE)
        print p.content
        assert p.status_code == 200
        print p.content


        #submit the job
        post_url = JOBS_URL + "/" + str(job_id) + "/submit"
        p = s.post(post_url, verify = PEM_CERTIFICATE)
        assert p.status_code == 200


        #wait for completion
        get_url = JOBS_URL + "/" + str(job_id) + "/state"
        p = s.get(get_url, verify = PEM_CERTIFICATE)
        assert p.status_code == 200
        state = p.content

        while state not in ['Done', 'Failed']:
            time.sleep(JOB_STATE_REFRESH_PERIOD)
            p = s.get(get_url, verify = PEM_CERTIFICATE)
            assert p.status_code == 200
            state = p.content

        # job has completed or failed. check to see if the job has been retrieved
        get_retrieved_state_url = JOBS_URL + "/" + str(job_id) + "/retrieved"
        p = s.get(get_retrieved_state_url, verify=PEM_CERTIFICATE)
        assert p.status_code == 200
        retrieved = int(p.content)


        while retrieved != 1:
            time.sleep(JOB_STATE_REFRESH_PERIOD)
            p = s.get(get_retrieved_state_url, verify=PEM_CERTIFICATE)
            assert p.status_code == 200
            retrieved = int(p.content)


        # get the list of output files
        file_list_url =  JOBS_URL + "/" + str(job_id) + "/files"
        p = s.get(file_list_url, verify=PEM_CERTIFICATE)
        assert p.status_code == 200
        file_list = p.json()

        # download the files
        for f in file_list:
            download_file(job_id, f, s)



        # delete the job
        delete_url = JOBS_URL + "/" + str(job_id)
        p = s.delete(delete_url, verify = PEM_CERTIFICATE)
        assert p.status_code == 200





def main():
    runJob()




if __name__ == "__main__":
    main()