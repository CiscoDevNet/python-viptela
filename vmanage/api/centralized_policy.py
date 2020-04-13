"""Cisco vManage Centralized Policy API Methods.
"""

from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class CentralizedPolicy(object):
    """vManage Centralized Policy API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Centralized Policy.

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

    def deactivate_centralized_policy(self, policyId):
        """Deactivates the current active centralized policy

        Args:
            policyId (str): ID of the active centralized policy
        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/vsmart/deactivate/{policyId}?confirm=true"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('POST')
        result = ParseMethods.parse_status(response)
        return result

    def delete_centralized_policy(self, policyId):
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

    def delete_policy_definition(self, definition, definitionId):
        """Deletes the specified policy definition which include:
        'control','mesh','hubandspoke','vpnmembershipgroup',
        'approute','data','cflowd'

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
        return result

    def get_centralized_policy(self):
        """Obtain a list of all configured centralized policies

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/policy/vsmart"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_policy_definition(self, definition):
        """Obtain a list of various policy definitions which include:
        'control','mesh','hubandspoke','vpnmembershipgroup',
        'approute','data','cflowd'

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
