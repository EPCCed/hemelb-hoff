import requests

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

files = { 'config.gmy': open('/home/ubuntu/config.gmy','rb'),
          'config.xml': open('/home/ubuntu/config.xml','rb')
        }


with requests.Session() as s:

    p = s.post(LOGIN_URL, data=params)
    # print the html returned or something more intelligent to see if it's a successful login page.
    print p.text

    # An authorised request.
    p = s.post('http://127.0.0.1:5000/jobs', json=payload)
    job_id = p.content
    print job_id

    #upload the input files
    file_url = 'http://127.0.0.1:5000/jobs/' + str(job_id) + "/files"
    p = s.post(file_url, files=files)
    print p.text

    #submit the job
    post_url = 'http://127.0.0.1:5000/jobs/' + str(job_id) + "/submit"
    p = s.post(post_url)
    print p.text


