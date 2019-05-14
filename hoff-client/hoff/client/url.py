class UrlBuildMixin(object):
    """Helper mixin for clients that need to build URLs from a base URL
    attribute.

    Make sure you set `url` attribute on subclasses before calling this.
    """

    def urlbuild(self, *parts):
        base = self.url
        for p in parts:
            if p.startswith("/"):
                p = p[1:]
            if base.endswith("/"):
                base += p
            else:
                base += "/" + p
        return base

    pass
