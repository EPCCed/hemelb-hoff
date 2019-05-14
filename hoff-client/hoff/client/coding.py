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

class JsonCodable(object):
    """Mixin to make things easy to move between JSON and objects,
    optionally renaming them.

    Subclasses must set JSON_ATTRS to an iterable of strings and
    JSON_RENAME_C2S as a (possibly empty) mapping with keys giving the
    client/object side name of attributes and values being the
    server/json-dict side name.
    """

    def __init__(self, **kwargs):
        for client_attr in self.JSON_ATTRS:
            server_attr = self.JSON_RENAME_C2S.get(client_attr, client_attr)
            setattr(self, client_attr, kwargs.pop(server_attr))
        if len(kwargs):
            raise ValueError("Unknown keyword arguments: " + str(list(kwargs.keys())))

    def json(self):
        ans = {}
        for client_attr in self.JSON_ATTRS:
            server_attr = self.JSON_RENAME_C2S.get(client_attr, client_attr)
            ans[server_attr] = getattr(self, client_attr)
        return ans

    pass
