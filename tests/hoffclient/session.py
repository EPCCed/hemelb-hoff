import requests
from .url import UrlBuildMixin

class Session(UrlBuildMixin):
    """Control a connection to the hoff-server
    
    Pass a Config instance to construct
    
    use login() and logout() or use as a context manager:
    
    with Session(conf) as s:
        # do stuff
        pass

    # Python ensures that logout is called when exiting the block
    """


    def __init__(self, config):
        """Pass a Config instance

        Note this doesn't actually connect - use login or with-statement
        """
        self._config = config
        self.url = config.server_url
        self._job_client = None

    def login(self):
        """Use credentials to log into the configured hoff-server."""
        # Create the session
        self.session = requests.Session()
        login_credentials = {
            'email': self._config.username,
            'password': self._config.password
        }
        # Use that to log into the Hoff
        resp = self.session.post(self.urlbuild("admin", "login/"),
                                     data=login_credentials)
        if resp.status_code == 200:
            return

        # Error!
        raise HoffError(
            'Could not log into the hoff-server "{}" as user "{}"'.format(self.BASE_URL, self._config.username),
            response=resp)

    def logout(self):
        """Disconnect from the server."""
        self.session.close()
        return

    def __enter__(self):
        """Login on starting a with statement."""
        self.login()
        return self
    def __exit__(self, *args):
        """Logout on exiting a with statement."""
        self.logout()

    @property
    def jobs(self):
        if self._job_client is None:
            from .jobs import JobClient
            self._job_client = JobClient(self.session, self.urlbuild("jobs"))
        return self._job_client

    pass

    
