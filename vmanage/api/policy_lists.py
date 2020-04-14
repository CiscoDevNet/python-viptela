"""Cisco vManage Policy Lists API Methods.
"""

import json
import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.api.device_templates import DeviceTemplates
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


class PolicyLists(object):
    """vManage Policy Lists API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Policy Lists used in Centralized, Localized, and Security Policy.

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
        self.policy_list_cache = {}

    def delete_data_prefix_list(self, listid):
        """Delete a Data Prefix List from vManage.

        Args:
            listid (str): vManaged assigned list identifier

        Returns:
            response (dict): Results from deletion attempt.

        """

        api = "template/policy/list/dataprefix/" + listid
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

    def get_data_prefix_list(self):
        """Get all Data Prefix Lists from vManage.

        Returns:
            response (dict): A list of all data prefix lists currently
                in vManage.

        """

        api = "template/policy/list/dataprefix"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        return response

    def get_policy_list_all(self):
        """Get all Policy Lists from vManage.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        api = "template/policy/list"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def post_data_prefix_list(self, name, entries):
        """Add a new Data Prefix List to vManage.

        Args:
            name (str): name of the data prefix list
            entries (list): a list of prefixes to add to the list

        Returns:
            response (dict): Results from attempting to add a new
                data prefix list.

        """

        api = "template/policy/list/dataprefix"
        url = self.base_url + api
        payload = f"{{'name':'{name}','type':'dataPrefix',\
            'listId':null,'entries':{entries}}}"

        response = HttpMethods(self.session, url).request('POST', payload=payload)
        result = ParseMethods.parse_status(response)
        return result

    def put_data_prefix_list(self, name, listid, entries):
        """Update an existing Data Prefix List on vManage.

        Args:
            name (str): name of the data prefix list
            listid (str): vManaged assigned list identifier
            entries (list): a list of prefixes to add to the list

        Returns:
            response (dict): Results from attempting to update an
                existing data prefix list.

        """

        api = f"template/policy/list/dataprefix/{listid}"
        url = self.base_url + api
        payload = f"{{'name':'{name}','type':'dataPrefix',\
            'listId':'{listid}','entries':{entries}}}"

        response = HttpMethods(self.session, url).request('PUT', payload=payload)
        result = ParseMethods.parse_status(response)
        return result

    def delete_policy_list(self, listType, listId):
        """Deletes the specified policy list type

        Args:
            listType (str): Policy list type
            listId (str): ID of the policy list

        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/list/{listType}/{listId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

    def clear_policy_list_cache(self):
        self.policy_list_cache = {}

    def get_policy_list_list(self, policy_list_type='all', cache=True):
        """Get a list of policy lists

        Args:
            policy_list_type (str): Policy list type
            cache (bool): Whether to cache the response

        Returns:
            result (dict): All data associated with a response.

        """
        if cache and policy_list_type in self.policy_list_cache:
            response = self.policy_list_cache[policy_list_type]
        else:
            if policy_list_type == 'all':
                api = f"template/policy/list"
                # result = self.request('/template/policy/list', status_codes=[200])
            else:
                api = f"template/policy/list/{policy_list_type.lower()}"
                # result = self.request('/template/policy/list/{0}'.format(type.lower()), status_codes=[200, 404])

            url = self.base_url + api
            response = HttpMethods(self.session, url).request('GET')

        if response['status_code'] == 404:
            return []

        self.policy_list_cache[policy_list_type] = response
        return response['json']['data']

    def get_policy_list_dict(self, policy_list_type='all', key_name='name', remove_key=False, cache=True):

        policy_list = self.get_policy_list_list(policy_list_type, cache=cache)

        return list_to_dict(policy_list, key_name, remove_key=remove_key)

    def add_policy_list(self, policy_list):
        """Add a new Policy List to vManage.

        Args:
            policy_list (dict): The Policy List

        Returns:
            response (dict): Results from attempting to add a new
                prefix list.

        """
        policy_list_type = policy_list['type'].lower()
        url = f"{self.base_url}template/policy/list/{policy_list_type}"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(policy_list))
        return ParseMethods.parse_status(response)

    def update_policy_list(self, policy_list):
        """Update an existing Policy List on vManage.

        Args:
            policy_list (dict): The Policy List

        Returns:
            response (dict): Results from attempting to update an
                existing data prefix list.

        """
        policy_list_type = policy_list['type'].lower()
        policy_list_id = policy_list['listId']
        url = f"{self.base_url}template/policy/list/{policy_list_type}/{policy_list_id}"
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy_list))
        ParseMethods.parse_status(response)
        return response

    #pylint: disable=unused-argument
    def import_policy_list_list(self, policy_list_list, push=False, update=False, check_mode=False, force=False):
        """Import a list of policy lists into vManage

        Args:
            policy_list_list: A list of polcies
            push (bool): Whether to push a change out
            update (bool): Whether to update when the list exists
            check_mode (bool): Report what updates would happen, but don't update

        Returns:
            result (dict): All data associated with a response.

        """

        # Policy Lists
        policy_list_updates = []
        #pylint: disable=too-many-nested-blocks
        for policy_list in policy_list_list:
            policy_list_dict = self.get_policy_list_dict(policy_list['type'], remove_key=False, cache=False)
            if policy_list['name'] in policy_list_dict:
                existing_list = policy_list_dict[policy_list['name']]
                diff = list(dictdiffer.diff(existing_list['entries'], policy_list['entries']))
                if diff:
                    policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
                if diff:
                    policy_list['listId'] = policy_list_dict[policy_list['name']]['listId']
                    # If description is not specified, try to get it from the existing information
                    if not policy_list['description']:
                        policy_list['description'] = policy_list_dict[policy_list['name']]['description']
                    if not check_mode and update:
                        response = self.update_policy_list(policy_list)

                        if response['json']:
                            # Updating the policy list returns a `processId` that locks the list and 'masterTemplatesAffected'
                            # that lists the templates affected by the change.
                            if 'error' in response['json']:
                                raise Exception(response['json']['error']['message'])
                            elif 'processId' in response['json']:
                                if push:
                                    vmanage_device_templates = DeviceTemplates(self.session, self.host)
                                    # If told to push out the change, we need to reattach each template affected by the change
                                    for template_id in response['json']['masterTemplatesAffected']:
                                        vmanage_device_templates.reattach_device_template(template_id)
                            else:
                                raise Exception("Did not get a process id when updating policy list")
            else:
                diff = list(dictdiffer.diff({}, policy_list))
                policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
                if not check_mode:
                    self.add_policy_list(policy_list)

        return policy_list_updates
