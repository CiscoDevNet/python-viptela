"""Cisco vManage Policy Definitions API Methods.
"""

import json

from vmanage.api.http_methods import HttpMethods
from vmanage.api.policy_lists import PolicyLists
from vmanage.data.parse_methods import ParseMethods
from vmanage.api.utilities import Utilities
from vmanage.utils import list_to_dict

definition_types_19_2_0 = [
    "data", "approute", "control", "cflowd", "mesh", "hubandspoke", "vpnmembershipgroup", "qosmap", "rewriterule",
    "acl", "aclv6", "vedgeroute", "zonebasedfw", "intrusionprevention", "urlfiltering", "advancedMalwareProtection",
    "dnssecurity"
]

definition_types_19_3_0 = [
    "data", "approute", "control", "cflowd", "mesh", "hubandspoke", "vpnmembershipgroup", "qosmap", "rewriterule",
    "acl", "aclv6", "deviceaccesspolicy", "deviceaccesspolicyv6", "vedgeroute", "zonebasedfw", "intrusionprevention",
    "urlfiltering", "advancedMalwareProtection", "dnssecurity", "ssldecryption", "fxoport", "fxsport", "fxsdidport",
    "dialpeer", "srstphoneprofile"
]

all_definition_types = list(set(definition_types_19_2_0) | set(definition_types_19_3_0))


class PolicyDefinitions(object):
    """vManage Policy Definitions API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Policy Definitions used in Centralized, Localized, and Security Policy.

    """
    def __init__(self, session, host, port=443):
        """Initialize Policy Lists object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.policy_lists = PolicyLists(self.session, self.host, self.port)

        version = Utilities(self.session, self.host, self.port).get_vmanage_version()
        if version >= '19.3.0':
            self.definition_types = definition_types_19_3_0
        else:
            self.definition_types = definition_types_19_2_0

    def get_definition_types(self):
        """Return the definition types for this version of vManage

        Args:

        Returns:
            result (list): List of definition types

        """

        return self.definition_types

    def delete_policy_definition(self, definition_type, definition_id):
        """Delete a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{definition_type.lower()}/{definition_id}"
        HttpMethods(self.session, url).request('DELETE')

    def add_policy_definition(self, policy_definition):
        """Delete a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{policy_definition['type'].lower()}"
        HttpMethods(self.session, url).request('POST', payload=json.dumps(policy_definition))

    def update_policy_definition(self, policy_definition, policy_definition_id):
        """Update a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{policy_definition['type'].lower()}/{policy_definition_id}"
        HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy_definition))

    def get_policy_definition(self, definition_type, definition_id):
        """Get a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{definition_type.lower()}/{definition_id}"
        response = HttpMethods(self.session, url).request('GET')

        policy_definition = response["json"]
        return policy_definition

    def get_policy_definition_list(self, definition_type='all'):
        """Get all Policy Definition Lists from vManage.

        Args:
            definition_type (string): The type of Definition List to retreive

        Returns:
            response (dict): A list of all definition lists currently
                in vManage.

        """

        if definition_type == 'all':
            all_definitions_list = []
            for def_type in self.definition_types:
                definition_list = self.get_policy_definition_list(def_type)
                if definition_list:
                    all_definitions_list.extend(definition_list)
            return all_definitions_list

        definition_list = []

        if definition_type == "advancedMalwareProtection":
            url = f"{self.base_url}template/policy/definition/{definition_type}"
        else:
            url = f"{self.base_url}template/policy/definition/{definition_type.lower()}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        for definition in result:
            definition_detail = self.get_policy_definition(definition_type, definition['definitionId'])
            if definition_detail:
                definition_list.append(definition_detail)
        return definition_list

    def get_policy_definition_dict(self, definition_type, key_name='name', remove_key=False):
        """Get all Policy Definition Lists from vManage.

        Args:
            definition_type (str): Policy definition type
            key_name (string): The name of the attribute to use as the dictionary key
            remove_key (boolean): Remove the search key from the element

        Returns:
            result (dict): All data associated with a response.

        """

        policy_definition_list = self.get_policy_definition_list(definition_type)
        return list_to_dict(policy_definition_list, key_name, remove_key=remove_key)
