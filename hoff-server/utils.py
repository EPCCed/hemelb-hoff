"""
   Copyright 2018-2019 EPCC, University Of Edinburgh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from __future__ import print_function
import hashlib
import os


def queryresult_to_array(keys, queryresult):

    d = []
    try:
        for q in queryresult:
            row = {}
            for k in keys:
                row[k] = getattr(q, k)
            d.append(row)
    except TypeError:
        row = {}
        for k in keys:
            row[k] = getattr(queryresult, k)
        d.append(row)
    return d


def queryresult_to_dict(keys, queryresult):

    d = {}
    try:
        for q in queryresult:
            row = {}
            for k in keys:
                row[k] = getattr(q, k)
            d.update(row)
    except TypeError:
        row = {}
        for k in keys:
            row[k] = getattr(queryresult, k)
        d.update(row)
    return d


def compute_hash_for_dir_contents(dir):

    hash_sha = hashlib.sha1()
    read_blocksize = 2 << 15

    dirFiles = os.listdir(dir)
    sorted(dirFiles)

    for f in dirFiles:
        # use os.walk to iterate someDir's contents recursively. No
        # need to implement recursion yourself if stdlib does it for you
        abspath = os.path.join(dir, f)
        with open(abspath) as f:
            buf = f.read(read_blocksize)
            while len(buf) > 0:
                hash_sha.update(buf)
                buf = f.read(read_blocksize)

    return hash_sha.hexdigest()


def main():
    print(compute_hash_for_dir_contents("/home/ubuntu/inputsets/11"))


if __name__ == "__main__":
    main()
