#!/usr/bin/python2.6

"""
rbget - Copyright 2010 Emilio Guijarro Cameros (cyberguijarro@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import httplib
import base64
import json
import getpass
import sys
import tempfile
import subprocess
import os

def git(diff):
    temporary = tempfile.mkstemp()[1]
    file = open(temporary, "w")
    file.write(diff)
    file.close()
    subprocess.Popen(["git", "apply", temporary]).wait()
    os.remove(temporary)

def patch(diff):
    temporary = tempfile.mkstemp()[1]
    file = open(temporary, "w+")
    file.write(diff)
    file.seek(0, os.SEEK_SET)
    subprocess.Popen(["patch"], stdin=file).wait()
    file.close()
    os.remove(temporary)

if len(sys.argv) > 2:
    # Process command-line arguments
    hostname = sys.argv[1]
    review = sys.argv[2]
    applywith = sys.argv[3]

    # Read ReviewBoard credentials
    sys.stdout.write("Username: ")
    username = sys.stdin.readline() 
    password = getpass.getpass()

    # Connect to host
    host = httplib.HTTPConnection(hostname)
    headers = {"Authorization": "Basic %s" % base64.b64encode("%s:%s" % (username.strip(), password))}
    host.request("GET", "/api/json/info/", None, headers)
    response = host.getresponse()
    payload = json.loads(response.read())

    if payload["stat"] == "ok":
        # Set session cookie
        cookie = response.getheader("Set-Cookie").split("=")[1].split(";")[0]
        headers = {"Cookie": "rbsessionid=%s" % cookie}
        
        # Read diff
        host.request("GET", "/r/%s/diff/raw/" % review, None, headers)
        response = host.getresponse()
        
        if response.status == httplib.OK:
            if applywith != "none":
                eval("%s(response.read())" % applywith)
            else:
                sys.stdout.write(response.read())
        else:
            exit("Unable to fetch diff data (%s %s)" % (response.status, response.reason))
    else:
        exit("Authentication error (%s %s)." % (payload["err"]["code"], payload["err"]["msg"]))
else:
    exit("Usage: %s host-name review-id [git|patch|none]" % sys.argv[0])
