"""Cisco vManage Security Policy API Methods.
"""

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
        return result

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
