# Copyright 2018-2019 EPCC, University Of Edinburgh

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
