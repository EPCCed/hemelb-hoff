# local test configuration parameters for testing a running instance of the Hoff

# assume we are testing against a local flask instance on port 5000
BASE_URL = "http://127.0.0.1:5000"


LOGIN_URL = BASE_URL + "/admin/login/"
JOBS_URL = BASE_URL + "/jobs"
INPUTSETS_URL = BASE_URL + "/inputsets"
PEM_CERTIFICATE = "/home/ubuntu/hoff-server.pem"

# local credentials we are going to use for main tests
login_credentials = {
    'email': "***",
   'password': "***"
}


# local credentials for two test users, to test that users cant conflict with each other
login_credentials_user_1 = {
    'email': '***',
    'password': '***'
}

login_credentials_user_2 = {
    'email': '***',
    'password': '***'
}


TEST_RESULTS_DIR = "/home/ubuntu/results"

# name of an existing template which can be used for realistic testing.
# note that this will consume real resource, so something not too cpu-heavy!
TEST_TEMPLATE_NAME = "cirrus_mouse_288"

# name of an existing template which can be used for quick testing, ie short wallclock
QUICK_TEMPLATE_NAME = "test_sharpen"
QUICK_TEMPLATE_UPLOAD_FILE = "/home/ubuntu/fuzzy.pgm"


TEST_UPLOAD_FILE="/home/ubuntu/test_data/Myh9KO_ret1_mask_corrected_tubed_smoothed.gmy'"
TEST_CONFIG_FILE="/home/ubuntu/test_data/bignshort.xml"
TEST_INPUT_NAME="config.xml"
