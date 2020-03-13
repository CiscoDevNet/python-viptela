"""Cisco vManage Localized Policy API Methods.

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


class LocalPolicy(object):
    """vManage Local Policy API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Local Policy.

    """

    def __init__(self, session, host, port=443):
        """Initialize Localized Policy object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    # Need to decide where this goes
    def list_to_dict(self, list, key_name, remove_key=True):
        dict = {}
        for item in list:
            if key_name in item:
                if remove_key:
                    key = item.pop(key_name)
                else:
                    key = item[key_name]

                dict[key] = item

        return dict

    def get_local_policy_list(self):
        """Get all Central Policies from vManage.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """
        api = "template/policy/vedge"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        local_policy_list = result
        for policy in local_policy_list:
            # This is to accommodate CLI policy
            try:
                json_policy = json.loads(policy['policyDefinition'])
                policy['policyDefinition'] = json_policy
            except:
                pass
            # policy['policyDefinition'] = json.loads(policy['policyDefinition'])
            self.convert_definition_id_to_name(policy['policyDefinition'])
        return local_policy_list

    def get_local_policy_dict(self, key_name='policyName', remove_key=False):

        local_policy_list = self.get_local_policy_list()

        return self.list_to_dict(local_policy_list, key_name, remove_key=remove_key)

    def import_local_policy(self, local_policy, update=False, push=False, check_mode=False, force=False):
        diff = []
        changes = False
        local_policy_dict = self.get_local_policy_dict(remove_key=False)
        payload = {
            'policyName': local_policy['policyName']
        }
        payload['policyDescription'] = local_policy['policyDescription']
        payload['policyType'] = local_policy['policyType']
        payload['policyDefinition'] = local_policy['policyDefinition']
        if payload['policyName'] in local_policy_dict:
            # A policy by that name already exists
            existing_policy = local_policy_dict[payload['policyName']]
            diff = list(dictdiffer.diff(existing_policy['policyDefinition'], payload['policyDefinition']))
            if len(diff):
                if 'policyDefinition' in payload:
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode and update:
                    self.request('/template/policy/vedge/{0}'.format(existing_policy['policyId']), method='PUT', payload=payload)
        else:
            diff = list(dictdiffer.diff({}, payload['policyDefinition']))
            if 'policyDefinition' in payload:
                # Convert list and definition names to template IDs
                self.convert_definition_name_to_id(payload['policyDefinition'])
            if not check_mode:
                self.request('/template/policy/vedge', method='POST', payload=payload)        
        return diff
