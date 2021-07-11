"""Cisco vManage Policy Lists API Methods.
"""

import json
import time
import sys
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class PolicyUpdates(object):
    """vManage Policy Updates API

    Responsible for POST and PUT methods against vManage
    Policy APIs used in Centralized, Localized, and Security Policy.

    """
    def __init__(self, session, host, port=443):
        """Initialize Policy Updates object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def get_device_ids(self, template_id):
        """GET vSmart device ids from vManage.

        Args:
            templateid (str): vManaged assigned template identifier.

        Returns:
            response (list): device ids list.

        """

        api = "template/device/config/attached/" + template_id
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        device_ids = []
        for device in result:
            device_ids.append(device['uuid'])

        return device_ids

    def get_device_inputs(self, template_id, device_ids):
        """GET vSmart device inputs from vManage.

        Args:
            templateid (str): vManage assigned template identifier.
            device_ids (list): vManage assigned device ids for vSmarts.

        Returns:
            response (dict): device inputs.

        """

        payload = {"templateId": template_id, "deviceIds": device_ids, "isEdited": True, "isMasterEdited": False}

        api = "template/device/config/input"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        result = ParseMethods.parse_data(response)

        for item in result:
            item['csv-templateId'] = template_id

        return result

    def get_policy_id(self, policy_type, policy_name):
        """GET vSmart device ids from vManage.

        Args:
            policy_type (str): vManage policy type i.e. approute, data, hubandspoke etc.
            policy_name (str): policy name for user needs policy id.

        Returns:
            response (str): vManage assigned policy id.

        """

        api = "template/policy/definition/" + policy_type
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        policy_id = ""

        for item in result:
            if item["name"] == policy_name:
                policy_id = item["definitionId"]
                break

        return policy_id

    def get_policy_definition(self, policy_type, policy_id):
        """GET vSmart device ids from vManage.

        Args:
            policy_type (str): vManage policy type i.e. approute, data, hubandspoke etc.
            policy_id (str): vManage assigned policy id.

        Returns:
            response (dict): policy definition.

        """

        api = "template/policy/definition/%s/%s" % (policy_type, policy_id)
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')

        return response['json']

    def update_policy_definition(self, policy_type, name, policy_id, policy_def, new_color, seq_name=None):
        """update policy definition

        Args:
            policy_type (str): vManage policy type i.e. approute, data, hubandspoke etc.
            policy_id (str): vManage assigned policy id.
            policy_def (dict): dict of data for policy updates to be done

        Returns:
            response (dict): policy definition.

        """
        #pylint: disable=too-many-nested-blocks
        for item1 in policy_def["sequences"]:
            if item1["sequenceName"] == seq_name or seq_name is None:
                for item2 in item1["actions"]:
                    if item2['type'] == 'slaClass':
                        for item3 in item2['parameter']:
                            if item3["field"] == 'preferredColor':
                                item3["value"] = new_color

        # Update policy app route policy

        payload = {
            "name": policy_def["name"],
            "type": policy_def["type"],
            "description": policy_def["description"],
            "sequences": policy_def["sequences"]
        }

        api = "template/policy/definition/%s/%s" % (policy_type.lower(), policy_id)
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(payload))

        if response['status_code'] == 200:
            master_templates_affected = response['json']['masterTemplatesAffected']
            if master_templates_affected:
                print("\nMaster templates affected: %s" % master_templates_affected)
            else:
                print("\nUpdated %s App Route policy successfully" % (name))
                sys.exit()
        else:
            error = response['error']
            result = response['details']
            raise Exception(f'{error}: {result}')

        # Get device uuid and csv variables for each template id which is affected by prefix list edit operation

        inputs = []

        for template_id in master_templates_affected:
            device_ids = self.get_device_ids(template_id)
            device_inputs = self.get_device_inputs(template_id, device_ids)
            inputs.append((template_id, device_inputs))

        device_template_list = []

        for (template_id, device_input) in inputs:
            device_template_list.append({'templateId': template_id, 'isEdited': True, 'device': device_input})

        #api for CLI template 'template/device/config/attachcli'

        api = 'template/device/config/attachfeature'

        url = self.base_url + api

        payload = {'deviceTemplateList': device_template_list}

        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))

        if response['status_code'] == 200:
            process_id = response['json']['id']
        else:
            error = response['error']
            result = response['details']
            raise Exception(f'{error}: {result}')

        api = 'device/action/status/' + process_id

        url = self.base_url + api

        while (1):
            time.sleep(10)
            response = HttpMethods(self.session, url).request('GET')
            if response['status_code'] == 200:
                if response['json']['summary']['status'] == "done":
                    if 'Success' in response['json']['summary']['count']:
                        print("\nUpdated %s App Route policy successfully" % (name))
                    elif 'Failure' in response['json']['summary']['count']:
                        print("\nFailed to update App route policy")
                    break
            else:
                error = response['error']
                result = response['details']
                raise Exception(f'{error}: {result}')
