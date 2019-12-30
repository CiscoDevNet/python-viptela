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
