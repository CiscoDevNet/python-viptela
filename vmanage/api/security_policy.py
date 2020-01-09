"""Cisco vManage Security Policy API Methods.

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

import json
import requests
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class SecurityPolicy(object):
    """vManage Security Policy API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Security Policy.

    """

    def __init__(self, session, host, port=443):
        """Initialize Security Policy object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def delete_security_definition(self, definition, definitionId):
        """Deletes the specified policy definition which include:
        'zonebasedfw','urlfiltering', 'dnssecurity','intrusionprevention',
        'advancedMalwareProtection' for 18.4.0 or greater
        and
        'zonebasedfw' for

        Args:
            definition (str): One of the above policy types
            definitionId (str): ID of the policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/definition/{definition}/{definitionId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return(result)

    def delete_security_policy(self, policyId):
        """Deletes the specified security policy

        Args:
            policyId (str): ID of the active security policy
        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/security/{policyId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return(result)

    def get_security_definition(self, definition):
        """Obtain a list of various security definitions which include:
        'zonebasedfw','urlfiltering','intrusionprevention',
        'advancedMalwareProtection', 'dnssecurity'

        Args:
            definition (str): One of the above policy types

        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/definition/{definition}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)

    def get_security_policy(self):
        """Obtain a list of all configured security policies

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/policy/security"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)
