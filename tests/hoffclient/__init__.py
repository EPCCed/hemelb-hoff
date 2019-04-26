import json
import os.path
import requests
from .session import Session

class HoffError(requests.RequestException):
    pass

class Config(object):
    """Get required configuration data to connect to a hoff-server and
    make available as attributes.

    These can be supplied by a JSON configuration file or by environment
    variables.
    
    See REQUIRED_ATTRS for the list; environment variable names are
    "HOFF_" + uppercase(attribute name).
    """

    REQUIRED_ATTRS = ['username', 'password', 'server_url']

    def __init__(self, config_file=None):
        if config_file is None:
            try:
                for attr in self.REQUIRED_ATTRS:
                    setattr(self, attr, os.environ['HOFF_' + attr.upper()])
            except KeyError:
                raise EnvironmentError("Must set all environment variables (HOFF_USERNAME, HOFF_PASSWORD, HOFF_SERVER_URL) to configure without file")
        else:
            with open(config_file, 'r') as f:
                c = json.load(f)
            for attr in self.REQUIRED_ATTRS:
                setattr(self, attr, c[attr])
    pass



