"""Cisco vManage Device Inventory API Methods.
"""

import json
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class Device(object):
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

        api = f"device/"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)

    def get_device_status_dict(self, key_name='host-name', remove_key=False):
        """Obtain a dict of specified device type

        Args:
            category (str): vedges or controllers

        Returns:
            result (dict): Device status
        """

        result = self.get_device_status_list()

        return self.list_to_dict(result.json, key_name=key_name, remove_key=remove_key)

    def get_device_status(self, value, key='system-ip'):
        """Get the status of a specific device

        Args:
            value string: The value of the key to match
            key (string): The key on which to match (e.g. system-ip)

        Returns:
            result (dict): Device status
        """

        api = f"device?{key}={value}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)

    def get_device_dict(self, key_name='host-name', remove_key=False):

        device_list = self.get_device_list()

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

    def get_device_config_list(self, type):
        """Get the config status of a list of devices

        Args:
            type (str): vedge or controller

        Returns:
            result (dict): All data associated with a response.
        """

        api = f"system/device/{type}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)

    def get_device_config_dict(self, type, key_name='host-name', remove_key=False):

        device_list = self.get_device_config_list(type)

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)