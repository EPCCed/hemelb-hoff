import requests
import time
LOGIN_URL = 'http://127.0.0.1:5000/admin/login/'


params = {
    'email': "admin",
    'password': "admin"
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


with requests.Session() as s:

    p = s.post(LOGIN_URL, data=params)
    # print the html returned or something more intelligent to see if it's a successful login page.
    print p.status_code

    # An authorised request.
    p = s.post('http://127.0.0.1:5000/jobs', json=payload)
    job_id = p.content
    print job_id

    #upload the small input files
    file_url = 'http://127.0.0.1:5000/jobs/' + str(job_id) + "/files"
    p = s.post(file_url, files=small_files)
    print p.status_code


    #submit the job
    post_url = 'http://127.0.0.1:5000/jobs/' + str(job_id) + "/submit"
    p = s.post(post_url)
    print p.text

    #wait for completion
    get_url = 'http://127.0.0.1:5000/jobs/' + str(job_id) + "/state"
    p = s.get(get_url)
    state = p.content

    while state not in ['Done', 'Failed']:
        time.sleep(60)
        p = s.get(get_url)
        state = p.content
        print state

    print "deleting job"
    delete_url = 'http://127.0.0.1:5000/jobs/' + str(job_id)
    p = s.delete(delete_url)
    print p.status_code

    print "checking deleted state"
    get_url = 'http://127.0.0.1:5000/jobs/' + str(job_id) + "/state"
    p = s.get(get_url)
    state = p.content
    print "final state is " + state