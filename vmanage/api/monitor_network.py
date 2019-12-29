"""Cisco vManage Monitor Networks API Methods.

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


class MonitorNetwork(object):
    """vManage Monitor Networks API

    Responsible for GET methods against vManage Real Time Monitoring
    for network devices.

    """

    def __init__(self, session, host, port=443):
        """Initialize Monitor Networks object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def error_handling(self, response):
        """Error Handling for Empty Data.

        Args:
            response (obj): Requests response object

        Returns:
            result (dict): All data associated with a response.

        Raises:
            Exception: Provides error message and details of issue.
        """

        if 'data' in response['json']:
            result = response['json']['data']
        else:
            error = response['error']
            result = response['details']
            raise Exception(f'{error}: {result}')
        return(result)

    def get_control_connections(self, system_ip):
        """Provides current control connections for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        api = "device/control/connections?deviceId=" + system_ip
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = self.error_handling(response)
        return(result)

    def get_control_connections_history(self, system_ip):
        """Provides control connections history for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        api = "device/control/connectionshistory?deviceId=" + system_ip
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = self.error_handling(response)
        return(result)

    def get_device_status(self, system_ip):
        """Provides status for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        api = "device?system-ip=" + system_ip
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = self.error_handling(response)
        return(result)
