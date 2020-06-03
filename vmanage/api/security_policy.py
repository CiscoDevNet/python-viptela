"""Cisco vManage Security Policy API Methods.
"""

import json

from vmanage.api.http_methods import HttpMethods
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


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
        self.policy_definitions = PolicyDefinitions(self.session, self.host)

    def add_security_policy(self, policy):
        """Add a Security Policy from vManage.

        Args:
            policy: The Security Policy

        Returns:
            result (dict): All data associated with a response.

        """
        url = f"{self.base_url}template/policy/security"
        HttpMethods(self.session, url).request('POST', payload=json.dumps(policy))

    def update_security_policy(self, policy, policy_id):
        """Update a Security from vManage.

        Args:
            policy: The Security Policy
            policy_id: The ID of the Security Policy to update

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/security/{policy_id}"
        HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy))

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
        return result

    def delete_security_definition(self, definition, definitionId):
        """Deletes the specified policy definition which include:
        'zonebasedfw','urlfiltering', 'dnssecurity','intrusionprevention',
        'advancedMalwareProtection' for 18.4.0 or greater
        and
        'zonebasedfw' for

        Args:
            definition (str): One of the above policy types
            definitionId (str): ID of the policy definitions

        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/definition/{definition}/{definitionId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

    def get_security_policy(self):
        """Obtain a list of all configured security policies

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/policy/security"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

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
        return result

    def get_security_policy_list(self):
        """Get all Security Policies from vManage.

        Returns:
            response (list): A list of all policy lists currently
                in vManage.

        """

        security_policy_list = self.get_security_policy()
        # We need to convert the policy definitions from JSON
        for policy in security_policy_list:
            try:
                json_policy = json.loads(policy['policyDefinition'])
                policy['policyDefinition'] = json_policy
            except Exception:  # TODO: figuring out better exception type to catch
                pass
        return security_policy_list

    def get_security_policy_dict(self, key_name='policyName', remove_key=False):
        """Get all Security Policies from vManage.

        Args:
            key_name (str): The name of the attribute to use as the key
            remove_key (bool): Remove the key from the dict (default: False)

        Returns:
            response (dict): A dict of all Security Policies currently
                in vManage.

        """

        security_policy_list = self.get_security_policy_list()

        return list_to_dict(security_policy_list, key_name, remove_key=remove_key)
