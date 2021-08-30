"""Cisco vManage Centralized Policy API Methods.
"""
import json

from vmanage.api.http_methods import HttpMethods
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


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

    def activate_central_policy(self, policy_name, policy_id):
        """Activates the current active centralized policy

        Args:
            policyId (str): ID of the active centralized policy

        Returns:
            action_id (str): The Action ID from the activation.

        """

        url = f"{self.base_url}template/policy/vsmart/activate/{policy_id}?confirm=true"
        payload = {'policyName': policy_name}
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        ParseMethods.parse_status(response)
        action_id = ParseMethods.parse_id(response)

        return action_id

    def reactivate_central_policy(self, policy_id):
        """reActivates the current active centralized policy

        Args:
            policyId (str): ID of the active centralized policy

        Returns:
            action_id (str): The Action ID from the activation.

        """

        url = f"{self.base_url}template/policy/vsmart/activate/{policy_id}?confirm=true"
        payload = {'isEdited': True}
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        ParseMethods.parse_status(response)
        action_id = ParseMethods.parse_id(response)

        return action_id

    def deactivate_central_policy(self, policy_id):
        """Deactivates the current active centralized policy

        Args:
            policyId (str): ID of the deactive centralized policy

        Returns:
            result (str): The Action ID from the activation.

        """

        url = f"{self.base_url}template/policy/vsmart/deactivate/{policy_id}?confirm=true"
        response = HttpMethods(self.session, url).request('POST')
        ParseMethods.parse_status(response)
        if 'json' in response and 'id' in response['json']:
            return response['json']['id']

        return None

    def add_central_policy(self, policy):
        """Delete a Central Policy from vManage.

        Args:
            policy: The Central Policy

        Returns:
            result (dict): All data associated with a response.

        """
        url = f"{self.base_url}template/policy/vsmart"
        HttpMethods(self.session, url).request('POST', payload=json.dumps(policy))

    def update_central_policy(self, policy, policy_id):
        """Update a Central from vManage.

        Args:
            policy: The Central Policy
            policy_id: The ID of the Central Policy to update

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vsmart/{policy_id}"
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy))
        return response

    def delete_central_policy(self, policyId):
        """Deletes the specified centralized policy

        Args:
            policyId (str): ID of the active centralized policy
        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/vsmart/{policyId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

    def get_central_policy(self):
        """Obtain a list of all configured central policies

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vsmart"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_central_policy_list(self):
        """Get all Central Policies from vManage.

        Returns:
            response (list): A list of all policy lists currently
                in vManage.

        """

        central_policy_list = self.get_central_policy()
        # We need to convert the policy definitions from JSON
        for policy in central_policy_list:
            try:
                json_policy = json.loads(policy['policyDefinition'])
                policy['policyDefinition'] = json_policy
            except Exception:  # TODO: figuring out better exception type to catch
                pass
        return central_policy_list

    def get_central_policy_dict(self, key_name='policyName', remove_key=False):
        """Get all Central Policies from vManage.

        Args:
            key_name (str): The name of the attribute to use as the key
            remove_key (bool): Remove the key from the dict (default: False)

        Returns:
            response (dict): A dict of all Central Policies currently
                in vManage.

        """

        central_policy_list = self.get_central_policy_list()

        return list_to_dict(central_policy_list, key_name, remove_key=remove_key)
