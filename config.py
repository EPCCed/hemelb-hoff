# Create dummy secrey key so we can use sessions
SECRET_KEY = '*********'

# Name of the MariaDB database we will use
DATABASE_FILE = 'compbiomed'

# the complete path to our running database
# note that the account used here should not have any schema modification permissions,
# ie no table drops or creation
SQLALCHEMY_DATABASE_URI = 'mysql://web:web@localhost/' + DATABASE_FILE


# Application logging file name
APP_LOGFILE = '/home/ubuntu/foo.log'

SQLALCHEMY_ECHO = False

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "*****************************"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True

# this must be false or the unit tests can't log in correctly
# set to true for production deployment
WTF_CSRF_ENABLED = False

# Location for holding input file before staging
INPUT_STAGING_AREA = '/home/ubuntu/jobs/input'

# Location for holding output files
OUTPUT_STAGING_AREA = '/home/ubuntu/jobs/output'

# local for holding input filesets
INPUTSET_STAGING_AREA = '/home/ubuntu/inputsets'


# Location for temnporary files
TEMP_FOLDER = "/home/ubuntu/temp"

# maximum number of jobs a user may have.
# DELETED jobs are not counted
MAX_USER_JOBS = 10