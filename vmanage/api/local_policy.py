"""Cisco vManage Localized Policy API Methods.
"""

import json

from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.api.policy_definitions import PolicyDefinitions
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
        self.policy_definitions = PolicyDefinitions(self.session, self.host)

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
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy))
        return response

    def delete_local_policy(self, policy_id):
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

    def get_local_policy(self):
        """Obtain a list of all configured local policies

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vedge"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_local_policy_list(self):
        """Get all Central Policies from vManage.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        local_policy_list = self.get_local_policy()
        for policy in local_policy_list:
            # This is to accommodate CLI policy
            try:
                json_policy = json.loads(policy['policyDefinition'])
                policy['policyDefinition'] = json_policy
            except Exception:
                pass
        return local_policy_list

    def get_local_policy_dict(self, key_name='policyName', remove_key=False):
        """Get all Local Policies from vManage.

        Args:
            key_name (str): The name of the attribute to use as the key
            remove_key (bool): Remove the key from the dict (default: False)

        Returns:
            response (dict): A dict of all Local Polices currently
                in vManage.

        """

        local_policy_list = self.get_local_policy_list()

        return list_to_dict(local_policy_list, key_name, remove_key=remove_key)
