"""Cisco vManage Device Inventory API Methods.

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
from vmanage.data.parse_methods import ParseMethods


class DeviceInventory(object):
    """vManage Device Inventory API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Device Inventory.

    """

    def __init__(self, session, host, port=443):
        """Initialize Device Inventory object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def list_to_dict(self, list, key_name, remove_key=True):
        dict = {}
        for item in list:
            if key_name in item:
                if remove_key:
                    key = item.pop(key_name)
                else:
                    key = item[key_name]

                dict[key] = item
            # else:
            #     self.fail_json(msg="key {0} not found in dictionary".format(key_name))

        return dict

#
# Devices
#
    def get_device_status_list(self):
        """Obtain a list of specified device type

        Args: None

        Returns:
            result (list): Device status
        """

        api = f"device"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result.json)

    def get_device_status_dict(self, key_name='host-name', remove_key=False):
        """Obtain a dict of specified device type

        Args:
            key_name (str): Name of the key on which to hash (e.g. host-name)
            remove_key (bool): Whether to remove the key from the hash

        Returns:
            result (dict): Device status
        """

        result = self.get_device_status_list()

        return self.list_to_dict(result.json, key_name=key_name, remove_key=remove_key)

    def get_device_status(self, value, key='system-ip'):
        """Obtain the status for a specific device

        Args:
            key (str): Name of the key on which to search (e.g. host-name)

        Returns:
            result (dict): Device status
        """

        api = f"device?{key}={value}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result.json)

    # def get_device_list(self):
    #     result = self.request('/device')

    #     try:
    #         return result['json']['data']
    #     except:
    #         return []

    def get_device_dict(self, key_name='host-name', remove_key=False):

        device_list = self.get_device_list()

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

    def get_device_by_device_ip(self, device_ip):
        result = self.request('/system/device/controllers?deviceIP={0}'.format(device_ip))        
        if 'data' in result['json'] and result['json']['data']:
            return result['json']['data']
        
        result = self.request('/system/device/vedges?deviceIP={0}'.format(device_ip))

        try:
            return result['json']['data']
        except:
            return {}

    def get_device_config(self, type, device_ip):
        result = self.request('/system/device/{0}?deviceIP={1}'.format(type, device_ip))        

        try:
            return result['json']['data'][0]
        except:
            return {}

    def get_device_config_list(self, type):
        result = self.request('/system/device/{0}'.format(type))

        try:
            return result['json']['data']
        except:
            return []

    def get_device_config_dict(self, type, key_name='host-name', remove_key=False):

        device_list = self.get_device_config_list(type)

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)



    def get_device_list(self, category):
        """Obtain a list of specified device type

        Args:
            category (str): vedges or controllers

        Returns:
            result (dict): All data associated with a response.
        """

        api = f"system/device/{category}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)

    def post_device_cli_mode(self, deviceId, deviceIP, deviceType):
        """Update a device to CLI mode

        Args:
            deviceId (str): uuid for device object
            deviceIP (str): system IP equivalent
            deviceType (str): vedge or controller

        """

        api = "template/config/device/mode/cli"
        url = self.base_url + api
        devices = f"{{'deviceId':'{deviceId}','deviceIP':'{deviceIP}'}}"
        payload = f"{{'deviceType':'{deviceType}','devices':[{devices}]}}"
        response = HttpMethods(self.session, url).request(
            'POST', payload=payload
            )
        result = ParseMethods.parse_status(response)
        return(result)
