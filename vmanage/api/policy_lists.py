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
from vmanage.api.http_methods import HttpMethods


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
        return(response)

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
        return(response)

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
        payload = f"{{'name':'{name}','type':'dataPrefix','listId':null,'entries':{entries}}}"
        response = HttpMethods(self.session, url).request('POST', payload=payload)
        return(response)

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

        api = "template/policy/list/dataprefix/" + listid
        url = self.base_url + api
        payload = f"{{'name':'{name}','type':'dataPrefix','listId':'{listid}','entries':{entries}}}"
        response = HttpMethods(self.session, url).request('PUT', payload=payload)
        return(response)
