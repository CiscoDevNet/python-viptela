"""Cisco vManage Device Templates API Methods.

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


class DeviceTemplates(object):
    """vManage Device Templates API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Device Templates.

    """

    def __init__(self, session, host, port=443):
        """Initialize Device Templates object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def delete_device_template(self, templateId):
        """Obtain a list of all configured device templates.

        Args:
            templateId (str): Object ID for device template

        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/device/{templateId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return(result)

    def get_device_templates(self):
        """Obtain a list of all configured device templates.

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/device"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)