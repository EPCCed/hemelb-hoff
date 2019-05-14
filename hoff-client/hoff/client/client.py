from .url import UrlBuildMixin


class SubClient(UrlBuildMixin):
    """Create subclasses for different things and don't create this
    yourself, get it from the Session object.
    """

    def __init__(self, session, url):
        self.session = session
        self.url = url

    pass
