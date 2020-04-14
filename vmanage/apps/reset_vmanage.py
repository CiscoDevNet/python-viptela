"""Reset vManage Application.
"""

import time
from vmanage.api.utilities import Utilities
from vmanage.api.centralized_policy import CentralizedPolicy
from vmanage.api.device_inventory import DeviceInventory
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.api.localized_policy import LocalizedPolicy
from vmanage.api.security_policy import SecurityPolicy
from vmanage.api.policy_lists import PolicyLists


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
        self.cen_pol = CentralizedPolicy(self.session, self.host)
        self.inventory = DeviceInventory(self.session, self.host)
        self.dev_temps = DeviceTemplates(self.session, self.host)
        self.fet_temps = FeatureTemplates(self.session, self.host)
        self.loc_pol = LocalizedPolicy(self.session, self.host)
        self.sec_pol = SecurityPolicy(self.session, self.host)
        self.pol_lists = PolicyLists(self.session, self.host)

    def active_count_delay(self):

        activeCount = 1
        while activeCount != 0:
            time.sleep(1.0)
            data = self.utilities.get_active_count()
            activeCount = data["activeTaskCount"]

    def execute(self):

        # Step 1 - Deactivate Centralized Policy
        data = self.cen_pol.get_centralized_policy()
        for policy in data:
            if policy['isPolicyActivated']:
                policyId = policy['policyId']
                self.cen_pol.deactivate_centralized_policy(policyId)
        self.active_count_delay()

        # Step 2 - Detach vedges from template
        data = self.inventory.get_device_list('vedges')
        for device in data:
            if (('deviceIP' in device) and (device['configOperationMode'] == 'vmanage')):
                deviceId = device['uuid']
                deviceIP = device['deviceIP']
                deviceType = device['deviceType']
                self.inventory.post_device_cli_mode(deviceId, deviceIP, deviceType)
        self.active_count_delay()

        # Step 3 - Detach controllers from template
        data = self.inventory.get_device_list('controllers')
        for device in data:
            if (('deviceIP' in device) and (device['configOperationMode'] == 'vmanage')):
                deviceId = device['uuid']
                deviceIP = device['deviceIP']
                deviceType = device['deviceType']
                self.inventory.post_device_cli_mode(deviceId, deviceIP, deviceType)
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
        data = self.fet_temps.get_feature_templates()
        for device in data:
            #pylint: disable=no-else-continue
            if device['factoryDefault']:
                continue
            else:
                templateId = device['templateId']
                self.fet_temps.delete_feature_template(templateId)
        self.active_count_delay()

        # Step 6 - Delete All Centralized Policies
        data = self.cen_pol.get_centralized_policy()
        for policy in data:
            policyId = policy['policyId']
            self.cen_pol.delete_centralized_policy(policyId)
        self.active_count_delay()

        # Step 7 - Delete All Topology, Traffic, Cflowd Policies
        definitionList = ['control', 'mesh', 'hubandspoke', 'vpnmembershipgroup', 'approute', 'data', 'cflowd']
        for definition in definitionList:
            data = self.cen_pol.get_policy_definition(definition)
            if data:
                for policy in data:
                    definitionId = policy['definitionId']
                    self.cen_pol.delete_policy_definition(definition, definitionId)
        self.active_count_delay()

        # Step 8 - Delete All Localized Policies
        data = self.loc_pol.get_localized_policy()
        for policy in data:
            policyId = policy['policyId']
            self.loc_pol.delete_localized_policy(policyId)
        self.active_count_delay()

        # Step 9 - Delete All Localized Specific Definitions
        definitionList = ['qosmap', 'rewriterule', 'acl', 'aclv6', 'vedgeroute']
        for definition in definitionList:
            data = self.loc_pol.get_localized_definition(definition)
            if data:
                for policy in data:
                    definitionId = policy['definitionId']
                    self.loc_pol.delete_localized_definition(definition, definitionId)
        self.active_count_delay()

        # Step 10 - Delete All Security Policies
        version = self.utilities.get_vmanage_version()
        if version >= '18.2.0':
            data = self.sec_pol.get_security_policy()
            for policy in data:
                policyId = policy['policyId']
                self.sec_pol.delete_security_policy(policyId)
            self.active_count_delay()

        # Step 11 - Delete All UTD Specific Security Policies
        version = self.utilities.get_vmanage_version()
        definitionList = []
        # TODO: implement a proper semver comparison, this will fail if version is 18.30.0
        if version >= '18.4.0':
            definitionList = [
                'zonebasedfw', 'urlfiltering', 'dnssecurity', 'intrusionprevention', 'advancedMalwareProtection'
            ]
        #pylint: disable=chained-comparison
        if version < '18.4.0' and version >= '18.2.0':
            definitionList = ['zonebasedfw']

        if definitionList:
            for definition in definitionList:
                data = self.sec_pol.get_security_definition(definition)
                if data:
                    for policy in data:
                        definitionId = policy['definitionId']
                        self.sec_pol.delete_security_definition(definition, definitionId)
        self.active_count_delay()

        # Step 12 - Delete All Lists

        data = self.pol_lists.get_policy_list_all()
        for policy_list in data:
            owner = policy_list['owner']

            if owner != 'system':
                listType = policy_list['type'].lower()
                listId = policy_list['listId']
                self.pol_lists.delete_policy_list(listType, listId)

        return ('Reset Complete')
