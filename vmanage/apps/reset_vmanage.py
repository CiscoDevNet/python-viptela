"""Reset vManage Application.

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
import time
from vmanage.api.utilities import Utilities
from vmanage.api.centralized_policy import CentralizedPolicy
from vmanage.api.device_inventory import DeviceInventory
from vmanage.api.device_templates import DeviceTemplates


class ResetVmanage(object):
    """Reset all configuratios on a vManage instance.

    Executes the necessary REST calls in specific order to remove
    configurations applied to a vManage instance.

    """

    def __init__(self, session, host, port=443):
        """Initialize Reset vManage object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.utilities = Utilities(self.session, self.host)
        self.cp = CentralizedPolicy(self.session, self.host)
        self.inventory = DeviceInventory(self.session, self.host)
        self.dev_temps = DeviceTemplates(self.session, self.host)

    def active_count_delay(self):

        activeCount = 1
        while activeCount != 0:
            time.sleep(1.0)
            data = self.utilities.get_active_count()
            activeCount = data["activeTaskCount"]

    def execute(self):

        # Step 1 - Deactivate Centralized Policy
        data = self.cp.get_centralized_policy()
        for policy in data:
            if policy['isPolicyActivated']:
                policyId = policy['policyId']
                self.cp.deactivate_centralized_policy(policyId)
        self.active_count_delay()

        # Step 2 - Detach vedges from template
        data = self.inventory.get_device_list('vedges')
        for device in data:
            if (
                ('deviceIP' in device) and
                (device['configOperationMode'] == 'vmanage')
            ):
                deviceId = device['uuid']
                deviceIP = device['deviceIP']
                deviceType = device['deviceType']
                self.inventory.post_device_cli_mode(
                    deviceId, deviceIP, deviceType
                )
        self.active_count_delay()

        # Step 3 - Detach controllers from template
        data = self.inventory.get_device_list('controllers')
        for device in data:
            if (
                ('deviceIP' in device) and
                (device['configOperationMode'] == 'vmanage')
            ):
                deviceId = device['uuid']
                deviceIP = device['deviceIP']
                deviceType = device['deviceType']
                self.inventory.post_device_cli_mode(
                    deviceId, deviceIP, deviceType
                )
                # Requires pause between controllers
                self.active_count_delay()
        self.active_count_delay()

        # Step 4 - Delete All Device Templates
        data = self.dev_temps.get_device_templates()
        for device in data:
            templateId = device['templateId']
            self.dev_temps.delete_device_template(templateId)
        self.active_count_delay()

        # Step 5 - Delete All Feature Templates

        # Step 6 - Delete All Centralized Policies

        # Step 7 - Delete All Localized Policies

        # Step 8 - Delete All Topology, Traffic, Cflowd Policies

        # Step 9 - Delete All Security Policies

        # Step 10 - Delete All Lists