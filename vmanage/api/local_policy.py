"""Cisco vManage Localized Policy API Methods.
"""

import json

import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


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

    def add_local_policy(self, policy):
        """Delete a Central Policy from vManage.

        Args:
            policy: The Central Policy

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vedge"
        HttpMethods(self.session, url).request('POST', payload=json.dumps(policy))

    def update_local_policy(self, policy, policy_id):
        """Update a Central from vManage.

        Args:
            policy: The Central Policy
            policy_id: The ID of the Central Policy to update

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vedge/{policy_id}"
        HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy))

    def delete_localized_policy(self, policy_id):
        """Deletes the specified local policy

        Args:
            policyId (str): ID of the active local policy
        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vedge/{policy_id}"
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

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
            except Exception:
                pass
            # policy['policyDefinition'] = json.loads(policy['policyDefinition'])
            self.convert_definition_id_to_name(policy['policyDefinition'])
        return local_policy_list

    def get_local_policy_dict(self, key_name='policyName', remove_key=False):

        local_policy_list = self.get_local_policy_list()

        return list_to_dict(local_policy_list, key_name, remove_key=remove_key)

    #pylint: disable=unused-argument
    def import_local_policy_list(self, local_policy_list, update=False, push=False, check_mode=False, force=False):
        local_policy_dict = self.get_local_policy_dict(remove_key=False)
        local_policy_updates = []
        for local_policy in local_policy_list:
            payload = {'policyName': local_policy['policyName']}
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
                        self.update_local_policy(payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                if 'policyDefinition' in payload:
                    # Convert list and definition names to template IDs
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode:
                    self.add_local_policy(payload)
        return local_policy_updates
