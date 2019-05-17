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

class BaseJob:
    def set_local_id(id):
        pass

    def get_local_id(self):
        pass

    def set_remote_id(id):
        pass

    def get_remote_id(self):
        pass

    def get_remote_state(self):
        pass

    def submit_job(self):
        pass

    def delete_job(self):
        pass

    def create_reservation(self):
        pass

    def delete_reservation(self):
        pass

    def submit_job(self, job_description, endpoint):
        pass
