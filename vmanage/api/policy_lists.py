"""Cisco vManage Policy Lists API Methods.

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
import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


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
        return(result)

    def get_data_prefix_list(self):
        """Get all Data Prefix Lists from vManage.

        Returns:
            response (dict): A list of all data prefix lists currently
                in vManage.

        """

        api = "template/policy/list/dataprefix"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        return(response)

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
        return(result)

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
        response = HttpMethods(self.session, url).request(
            'POST', payload=payload
        )
        result = ParseMethods.parse_status(response)
        return(result)

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
        response = HttpMethods(self.session, url).request(
            'PUT', payload=payload
        )
        result = ParseMethods.parse_status(response)
        return(result)

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
        return(result)

#
# Orig
#
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

    def clear_policy_list_cache(self):
        self.policy_list_cache = {}

    def get_policy_list_list(self, type='all', cache=True):
        """Get a list of policy lists

        Args:
            type (str): Policy list type
            cache (bool): Whether to cache the response

        Returns:
            result (dict): All data associated with a response.

        """
        if cache and type in self.policy_list_cache:
            response = self.policy_list_cache[type]
        else:
            if type == 'all':
                api = f"template/policy/list"
                # result = self.request('/template/policy/list', status_codes=[200])
            else:
                api = f"template/policy/list/{type.lower()}"
                # result = self.request('/template/policy/list/{0}'.format(type.lower()), status_codes=[200, 404])

            url = self.base_url + api
            response = HttpMethods(self.session, url).request('GET')

        if response['status_code'] == 404:
            return []
        else:
            self.policy_list_cache[type] = response
            return response['json']['data']

    def get_policy_list_dict(self, type='all', key_name='name', remove_key=False, cache=True):

        policy_list = self.get_policy_list_list(type, cache=cache)

        return self.list_to_dict(policy_list, key_name, remove_key=remove_key)

    def add_prefix_list(self, policy_list):
        """Add a new Prefix List to vManage.

        Args:
            name (str): name of the data prefix list
            entries (list): a list of prefixes to add to the list

        Returns:
            response (dict): Results from attempting to add a new
                prefix list.

        """
        type = policy_list['type'].lower()
        api = "template/policy/list/{type}"
        url = self.base_url + api
        return HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))

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
        response = HttpMethods(self.session, url).request(
            'PUT', payload=payload
        )
        result = ParseMethods.parse_status(response)
        return(result)

    def import_policy_list(self, policy_list, push=False, update=False, check_mode=False, force=False):
        """Import policy list into vManage

        Args:
            listType (str): Policy list type
            listId (str): ID of the policy list

        Returns:
            result (dict): All data associated with a response.

        """
        diff = []
        # Policy Lists
        policy_list_dict = self.get_policy_list_dict(policy_list['type'], remove_key=False, cache=False)
        if policy_list['name'] in policy_list_dict:
            existing_list = policy_list_dict[policy_list['name']]
            diff = list(dictdiffer.diff(existing_list['entries'], policy_list['entries']))
            if diff:
                policy_list['listId'] = policy_list_dict[policy_list['name']]['listId']
                # If description is not specified, try to get it from the existing information
                if not policy_list['description']:
                    policy_list['description'] = policy_list_dict[policy_list['name']]['description']
                if not check_mode and update:
                    policy_list_type = policy_list['type'].lower()
                    policy_list_id = policy_list['listId']
                    url = f"{self.base_url}template/policy/list/{policy_list_type}/{policy_list_id}"
                    response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy_list))

                    if response['json']:
                        # Updating the policy list returns a `processId` that locks the list and 'masterTemplatesAffected'
                        # that lists the templates affected by the change.
                        if 'error' in response['json']:
                            raise Exception(response['json']['error']['message'])
                        elif 'processId' in response['json']:
                            process_id = response['json']['processId']
                            if push:
                                # If told to push out the change, we need to reattach each template affected by the change
                                for template_id in response['json']['masterTemplatesAffected']:
                                    action_id = self.reattach_device_template(template_id)
                        else:
                            raise Exception("Did not get a process id when updating policy list")
        else:
            diff = list(dictdiffer.diff({}, policy_list))
            if not check_mode:
                policy_list_type = policy_list['type'].lower()
                url = f"{self.base_url}template/policy/list/{policy_list_type}"
                response = HttpMethods(self.session, url).request('POST', payload=json.dumps(policy_list))
        return diff