"""Cisco vManage Centralized Policy API Methods.
"""

import json
import requests
import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.api.policy_definitions import PolicyDefinitions


class CentralPolicy(object):
    """vManage Central Policy API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Central Policy.

    """

    def __init__(self, session, host, port=443):
        """Initialize Centralized Policy object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.policy_definitions = PolicyDefinitions(self.session, self.host)

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

    def get_central_policy_list(self):
        """Get all Central Policies from vManage.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        api = "template/policy/vsmart"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        central_policy_list = result
        # We need to convert the policy definitions from JSON
        for policy in central_policy_list:
            try:
                json_policy = json.loads(policy['policyDefinition'])
                policy['policyDefinition'] = json_policy
            except:
                pass
            self.policy_definitions.convert_definition_id_to_name(policy['policyDefinition'])
        return central_policy_list


    def get_central_policy_dict(self, key_name='policyName', remove_key=False):

        central_policy_list = self.get_central_policy_list()

        return self.list_to_dict(central_policy_list, key_name, remove_key=remove_key)

    def import_central_policy(self, central_policy, update=False, push=False, check_mode=False, force=False):
        policy_definitions = PolicyDefinitions(self.session, self.host, self.port)

        diff = []
        central_policy_dict = self.get_central_policy_dict(remove_key=True)
        payload = {
            'policyName': central_policy['policyName']
        }
        payload['policyDescription'] = central_policy['policyDescription']
        payload['policyType'] = central_policy['policyType']
        payload['policyDefinition'] = central_policy['policyDefinition']
        if payload['policyName'] in central_policy_dict:
            # A policy by that name already exists
            existing_policy = central_policy_dict[payload['policyName']]
            diff = list(dictdiffer.diff(existing_policy['policyDefinition'], payload['policyDefinition']))
            if len(diff):
                # Convert list and definition names to template IDs
                if 'policyDefinition' in payload:
                    policy_definitions.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode and update:
                    url = f"{self.base_url}template/policy/vsmart/{existing_policy['policyId']}"
                    response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(payload))
        else:
            diff = list(dictdiffer.diff({}, payload['policyDefinition']))
            if not check_mode:
                # Convert list and definition names to template IDs
                if 'policyDefinition' in payload:
                    policy_definitions.convert_definition_name_to_id(payload['policyDefinition'])
                url = f"{self.base_url}template/policy/vsmart"
                response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))    
        return diff