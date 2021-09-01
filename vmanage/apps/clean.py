"""Clean vManage Resources.
"""

import time
from vmanage.api.utilities import Utilities
from vmanage.api.central_policy import CentralPolicy
from vmanage.api.device import Device
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.api.local_policy import LocalPolicy
from vmanage.api.security_policy import SecurityPolicy
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.api.policy_lists import PolicyLists


class CleanVmanage(object):
    """Reset all configurations on a vManage instance.

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
        self.central_policy = CentralPolicy(self.session, self.host)
        self.local_policy = LocalPolicy(self.session, self.host)
        self.device = Device(self.session, self.host)
        self.device_templates = DeviceTemplates(self.session, self.host)
        self.feature_templates = FeatureTemplates(self.session, self.host)
        self.sec_pol = SecurityPolicy(self.session, self.host)
        self.policy_definitions = PolicyDefinitions(self.session, self.host)
        self.policy_lists = PolicyLists(self.session, self.host)

    def active_count_delay(self):
        """Delay while there are active tasks.

        """
        activeCount = 1
        while activeCount != 0:
            time.sleep(1.0)
            data = self.utilities.get_active_count()
            activeCount = data["activeTaskCount"]

    def clean_vedge_attachments(self):
        """Clean all vedge attachments

        """
        data = self.device.get_device_list('vedges')
        for device in data:
            if (('uuid' in device) and (device['configOperationMode'] == 'vmanage')):
                deviceId = device['uuid']
                deviceType = device['deviceType']
                self.device.post_device_cli_mode(deviceId, deviceType)
        self.active_count_delay()

    def clean_vedge(self):
        """Clean all vedges

        """
        data = self.device.get_device_list('vedges')
        for device in data:
            if ('uuid' in device):
                deviceId = device['uuid']
                self.device.put_decommission_device(deviceId)
        self.active_count_delay()

    def clean_controller_attachments(self):
        """Clean all controller attachments

        """
        data = self.device.get_device_list('controllers')
        for device in data:
            if (('uuid' in device) and (device['configOperationMode'] == 'vmanage')):
                deviceId = device['uuid']
                deviceType = device['deviceType']
                self.device.post_device_cli_mode(deviceId, deviceType)
                # Requires pause between controllers
                self.active_count_delay()
        self.active_count_delay()

    def clean_device_templates(self):
        """Clean all device templates

        """
        data = self.device_templates.get_device_templates()
        for device in data:
            if 'factoryDefault' in device and device['factoryDefault'] is not True:
                templateId = device['templateId']
                self.device_templates.delete_device_template(templateId)
        self.active_count_delay()

    def clean_feature_templates(self):
        """Clean all feature templates

        """
        data = self.feature_templates.get_feature_templates()
        for device in data:
            #pylint: disable=no-else-continue
            if device['factoryDefault']:
                continue
            else:
                templateId = device['templateId']
                self.feature_templates.delete_feature_template(templateId)
        self.active_count_delay()

    def clean_central_policy(self):
        """Clean all central policy

        """
        data = self.central_policy.get_central_policy()
        for policy in data:
            policy_id = policy['policyId']
            if policy['isPolicyActivated']:
                action_id = self.central_policy.deactivate_central_policy(policy_id)
                if action_id:
                    self.utilities.waitfor_action_completion(action_id)
            self.central_policy.delete_central_policy(policy_id)
        self.active_count_delay()

    def clean_local_policy(self):
        """Clean all local policy

        """
        data = self.local_policy.get_local_policy()
        for policy in data:
            policyId = policy['policyId']
            self.local_policy.delete_local_policy(policyId)
        self.active_count_delay()

    def clean_policy_definitions(self):
        """Clean all policy definitions

        """
        policy_definition_list = self.policy_definitions.get_policy_definition_list()
        for policy_definition in policy_definition_list:
            self.policy_definitions.delete_policy_definition(policy_definition['type'],
                                                             policy_definition['definitionId'])
        self.active_count_delay()

    def clean_policy_lists(self):
        """Clean all policy lists

        """
        policy_list_list = self.policy_lists.get_policy_list_list()
        for policy_list in policy_list_list:
            if not policy_list['readOnly'] and policy_list['owner'] != 'system':
                self.policy_lists.delete_policy_list(policy_list['type'], policy_list['listId'])
        self.active_count_delay()

    def clean_security_policy(self):
        """Clean all security policy

        """
        version = self.utilities.get_vmanage_version()
        if version >= '18.2.0':
            data = self.sec_pol.get_security_policy()
            for policy in data:
                policyId = policy['policyId']
                self.sec_pol.delete_security_policy(policyId)
            self.active_count_delay()

        # # Step 11 - Delete All UTD Specific Security Policies
        # version = self.utilities.get_vmanage_version()
        # definitionList = []
        # # TODO: implement a proper semver comparison, this will fail if version is 18.30.0
        # if version >= '18.4.0':
        #     definitionList = [
        #         'zonebasedfw', 'urlfiltering', 'dnssecurity', 'intrusionprevention', 'advancedMalwareProtection'
        #     ]
        # #pylint: disable=chained-comparison
        # if version < '18.4.0' and version >= '18.2.0':
        #     definitionList = ['zonebasedfw']

        # if definitionList:
        #     for definition in definitionList:
        #         data = self.sec_pol.get_security_definition(definition)
        #         if data:
        #             for policy in data:
        #                 definitionId = policy['definitionId']
        #                 self.sec_pol.delete_security_definition(definition, definitionId)
        # self.active_count_delay()

        # # Step 12 - Delete All Lists

        # data = self.pol_lists.get_policy_list_all()
        # for policy_list in data:
        #     owner = policy_list['owner']

        #     if owner != 'system':
        #         listType = policy_list['type'].lower()
        #         listId = policy_list['listId']
        #         self.pol_lists.delete_policy_list(listType, listId)

    def clean_all(self):
        """Clean everything in vManage

        """
        # Step 1 - Deactivate Central Policy
        self.clean_central_policy()

        # Step 2 - Detach vedges from template
        self.clean_vedge_attachments()

        # Step 2 - Decommission vedges
        self.clean_vedge()

        # Step 3 - Detach controllers from template
        self.clean_controller_attachments()

        # Step 4 - Delete All Device Templates
        self.clean_device_templates()

        # Step 5 - Delete All Feature Templates
        self.clean_feature_templates()

        # Step 6 - Delete All Centralized Policies
        self.clean_central_policy()

        # Step 7 - Delete All Policy Definitions
        self.clean_policy_definitions()

        # Step 8 - Delete All Policy Lists
        self.clean_policy_lists()

        # Step 9 - Delete All Local Policies
        self.clean_local_policy()

        # Step 10 - Delete All Security Policies
        self.clean_security_policy()

        return ('Reset Complete')
