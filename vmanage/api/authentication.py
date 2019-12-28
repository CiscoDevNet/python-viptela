"""Cisco vManage Authentication API Methods.

MIT License

Copyright (c) 2019 Cisco Systems and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import (
    absolute_import,
    division,
    print_function
)

import json
import requests
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Authentication(object):
    def __init__(
        self, host=None, user=None, password=None, port=443,
        validate_certs=False, disable_warnings=False, timeout=10
    ):
        self.headers = dict()
        self.cookies = None
        self.json = None
        self.method = None
        self.path = None
        self.response = None
        self.status = None
        self.url = None
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.timeout = os.getenv('VMANAGE_TIMEOUT', timeout)
        self.base_url = 'https://{0}:{1}/dataservice'.format(self.host, self.port)
        self.session = requests.Session()
        self.session.verify = validate_certs
        self.policy_list_cache = {}

    def login(self):
        
        try:
            response = self.session.post(
                url='{0}/j_security_check'.format(self.base_url),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'j_username': self.user, 'j_password': self.password},
                timeout=self.timeout
            )

        except requests.exceptions.RequestException as e:
            raise Exception('Could not connect to {0}: {1}'.format(self.host, e))

        if response.status_code != 200 or response.text.startswith('<html>'):
            raise Exception('Could not login to device, check user credentials.')

        response = self.session.get(
            url='https://{0}/dataservice/client/token'.format(self.host),
            timeout=self.timeout
        )
        if response.status_code == 200:
            self.session.headers['X-XSRF-TOKEN'] = response.content
            
        elif response.status_code == 404:
            # Assume this is pre-19.2
            pass
        else:
            raise Exception('Failed getting X-XSRF-TOKEN: {0}'.format(response.status_code))

        
        return(self.session)