"""Cisco vManage Device Templates API Methods.
"""

import json
import re
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict
from vmanage.api.utilities import Utilities


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
        self.feature_templates = FeatureTemplates(self.session, self.host, self.port)

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
        return result

    def get_device_templates(self):
        """Obtain a list of all configured device templates.

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/device"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    #
    # Templates
    #
    def get_device_template_object(self, template_id):
        """Obtain a device template object.

        Args:
            template_id (str): Object ID for device template

        Returns:
            result (dict): All data associated with a response.
        """

        api = f"template/device/object/{template_id}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        if 'json' in response:
            return response['json']

        return {}

    def get_device_template_list(self, factory_default=False, name_list=None):
        """Get the list of device templates.

        Args:
            factory_default (bool): Include factory default
            name_list (list of strings): A list of template names to retreive.

        Returns:
            result (dict): All data associated with a response.
        """
        if name_list is None:
            name_list = []
        device_templates = self.get_device_templates()
        return_list = []

        #pylint: disable=too-many-nested-blocks
        for device in device_templates:
            # If there is a list of template name, only return the ones asked for.
            # Otherwise, return them all
            if name_list and device['templateName'] not in name_list:
                continue
            obj = self.get_device_template_object(device['templateId'])
            if obj:
                if not factory_default and obj['factoryDefault']:
                    continue
                obj['templateId'] = device['templateId']

                # obj['attached_devices'] = self.get_template_attachments(device['templateId'])
                # obj['input'] = self.get_template_input(device['templateId'])
                return_list.append(obj)
        return return_list

    def get_device_template_dict(self, factory_default=False, key_name='templateName', remove_key=True, name_list=None):
        """Obtain a dictionary of all configured device templates.


        Args:
            factory_default (bool): Wheter to return factory default templates
            key_name (string): The name of the attribute to use as the dictionary key
            remove_key (boolean): remove the search key from the element
            name_list (list of strings): A list of template names to retreive.

        Returns:
            result (dict): All data associated with a response.

        """
        if name_list is None:
            name_list = []
        device_template_list = self.get_device_template_list(factory_default=factory_default, name_list=name_list)

        return list_to_dict(device_template_list, key_name, remove_key)

    def get_template_attachments(self, template_id, key='host-name'):
        """Get the devices that a template is attached to.

        Args:
            template_id (string): Template ID
            key (string): The key of the device to put in the list (default: host-name)

        Returns:
            result (list): List of keys.

        """
        url = f"{self.base_url}template/device/config/attached/{template_id}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        attached_devices = []
        for device in result:
            attached_devices.append(device[key])

        return attached_devices

    def get_template_input(self, template_id, device_id_list=None):
        """Get the input associated with a device attachment.

        Args:
            template_id (string): Template ID
            device_id_list (list): list of device UUID's to get input for

        Returns:
            result (dict): All data associated with a response.

        """

        if device_id_list:
            deviceIds = device_id_list
        else:
            deviceIds = []
        payload = {"deviceIds": deviceIds, "isEdited": False, "isMasterEdited": False, "templateId": template_id}
        return_dict = {"columns": [], "data": []}

        url = f"{self.base_url}template/device/config/input"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))

        if 'json' in response:
            if 'header' in response['json'] and 'columns' in response['json']['header']:
                column_list = response['json']['header']['columns']

                regex = re.compile(r'\((?P<variable>[^(]+)\)$')

                for column in column_list:
                    if column['editable']:
                        match = regex.search(column['title'])
                        if match:
                            variable = match.groups('variable')[0]
                        else:
                            # If the variable is not found, use toolTip as variable name
                            variable = column.get("toolTip")

                        entry = {'title': column['title'], 'property': column['property'], 'variable': variable}
                        return_dict['columns'].append(entry)
            if 'data' in response['json'] and response['json']['data']:
                return_dict['data'] = response['json']['data']

        return return_dict

    def add_device_template(self, device_template):
        """Add a single device template to Vmanage.

        Args:
            device_template (dict): Device Template

        Returns:
            result (list): Response from Vmanage

        """
        payload = {
            'templateName': device_template['templateName'],
            'templateDescription': device_template['templateDescription'],
            'deviceType': device_template['deviceType'],
            'factoryDefault': device_template['factoryDefault'],
            'configType': device_template['configType'],
            'featureTemplateUidRange': []
        }
        if 'policyId' in device_template:
            payload['policyId'] = device_template['policyId']
        else:
            payload['policyId'] = ''
        if 'securityPolicyId' in device_template:
            payload['securityPolicyId'] = device_template['securityPolicyId']
        else:
            payload['securityPolicyId'] = ''

        #
        # File templates are much easier in that they are just a bunch of CLI
        #
        if device_template['configType'] == 'file':
            payload['templateConfiguration'] = device_template['templateConfiguration']
            url = f"{self.base_url}template/device/cli"
            response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        #
        # Feature based templates are just a list of templates Id that make up a devie template.  We are
        # given the name of the feature templates, but we need to translate that to the template ID
        #
        else:
            payload['generalTemplates'] = device_template['generalTemplates']
            url = f"{self.base_url}template/device/feature"
            response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        return response

    def update_device_template(self, device_template):
        """Update a single device template to Vmanage.

        Args:
            device_template (dict): Device Template

        Returns:
            result (list): Response from Vmanage

        """
        #
        # File templates are much easier in that they are just a bunch of CLI
        #
        # I'm not sure where this api call was found, but I can't find it in any doc and it doesn't currently work
        # if device_template['configType'] == 'file':
        #     url = f"{self.base_url}template/device/cli/{device_template['templateId']}"
        #     response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(device_template))
        #     ParseMethods.parse_data(response)
        #
        # Feature based templates are just a list of templates Id that make up a device template.  We are
        # given the name of the feature templates, but we need to translate that to the template ID
        #
        #else:
        url = f"{self.base_url}template/device/{device_template['templateId']}"
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(device_template))
        ParseMethods.parse_data(response)
        return response

    def reattach_device_template(self, template_id, config_type, is_edited=True, is_master_edited=True, wait=True):
        """Re-Attach a template to the devices it it attached to.

        Args:
            template_id (str): The template ID to attach to
            config_type (str): Type of template i.e. device or CLI template
            is_edited (bool): True if the template has been edited
            is_master_edited (bool): For CLI device template needs to match is_edited.
                    For device templates using feature templates needs to be set to False.

        Returns:
            action_id (str): Returns the action id of the attachment

        """
        device_list = self.get_template_attachments(template_id, key='uuid')
        template_input = self.get_template_input(template_id, device_list)

        # Then we feed that to the attach
        if 'data' in template_input and template_input['data']:
            payload = {
                "deviceTemplateList": [{
                    "templateId": template_id,
                    "device": template_input['data'],
                    "isEdited": is_edited,
                    "isMasterEdited": is_master_edited
                }]
            }
            if config_type == 'file':
                url = f"{self.base_url}template/device/config/attachcli"
            elif config_type == 'template':
                url = f"{self.base_url}template/device/config/attachfeature"
            else:
                raise RuntimeError('Got invalid Config Type')

            utils = Utilities(self.session, self.host, self.port)
            response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
            action_id = ParseMethods.parse_id(response)
            if wait:
                utils.waitfor_action_completion(action_id)
        else:
            raise RuntimeError(f"Could not retrieve input for template {template_id}")
        return action_id

    def attach_to_template(self, template_id, config_type, uuid, wait=True):
        """Attach and device to a template

        Args:
            template_id (str): The template ID to attach to
            config_type (str): Type of template i.e. device or CLI template
            uuid (dict): The UUIDs of the device to attach and mapping for corresponding variables, system-ip, host-name

        Returns:
            action_id (str): Returns the action id of the attachment

        """
        # Construct the variable payload

        device_template_var_list = list()
        template_variables = self.get_template_input(template_id)

        for device_uuid in uuid:

            device_template_variables = {
                "csv-status": "complete",
                "csv-deviceId": device_uuid,
                "csv-deviceIP": uuid[device_uuid]['system_ip'],
                "csv-host-name": uuid[device_uuid]['host_name'],
                '//system/host-name': uuid[device_uuid]['host_name'],
                '//system/system-ip': uuid[device_uuid]['system_ip'],
                '//system/site-id': uuid[device_uuid]['site_id'],
            }

            # Make sure they passed in the required variables and map
            # variable name -> property mapping

            for entry in template_variables['columns']:
                if entry['variable']:
                    if entry['variable'] in uuid[device_uuid]['variables']:
                        device_template_variables[entry['property']] = uuid[device_uuid]['variables'][entry['variable']]
                    elif entry['property'] in uuid[device_uuid]['variables']:
                        device_template_variables[entry['property']] = uuid[device_uuid]['variables'][entry['property']]
                    else:
                        raise RuntimeError(
                            f"{entry['variable']} is missing for template {uuid[device_uuid]['host_name']}")

            device_template_var_list.append(device_template_variables)

        payload = {
            "deviceTemplateList": [{
                "templateId": template_id,
                "device": device_template_var_list,
                "isEdited": False,
                "isMasterEdited": False
            }]
        }

        if config_type == 'file':
            url = f"{self.base_url}template/device/config/attachcli"
        elif config_type == 'template':
            url = f"{self.base_url}template/device/config/attachfeature"
        else:
            raise RuntimeError('Got invalid Config Type')

        utils = Utilities(self.session, self.host, self.port)
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        action_id = ParseMethods.parse_id(response)
        if wait:
            utils.waitfor_action_completion(action_id)

        return action_id

    def detach_from_template(self, uuid, device_ip, device_type):
        """Detach a device from a template (i.e. Put in CLI mode)

        Args:
            uuid (str): The UUID of the device to detach
            device_ip (str): The System IP of the system to detach
            device_type (str): The device type of the device to detach

        Returns:
            action_id (str): Returns the action id of the attachment

        """
        payload = {
            "deviceType": device_type,
            "devices": [{
                "deviceId": uuid,
                "deviceIP": device_ip,
            }]
        }
        url = f"{self.base_url}template/config/device/mode/cli"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        ParseMethods.parse_status(response)
        action_id = ParseMethods.parse_id(response)

        return action_id

    def get_attachments(self, template_id, key='host-name'):
        """Get a list of attachments to a particular template.

        Args:
            template_id (str): Template ID of the template
            key (str): The key of the elements to return

        Returns:
            result (list): Returns the specified key of the attached devices.

        """
        url = f"{self.base_url}template/device/config/attached/{template_id}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        attached_devices = []
        for device in result:
            attached_devices.append(device[key])

        return attached_devices

    def get_device_running_config(self, uuid):
        """
        Get the running configuration of a specific device.

        Args:
            uuid (str): UUID of device
        Returns:
            result (str): The running configuration of the specified device.
        """
        url = f"{self.base_url}template/config/running/{uuid}"
        response = HttpMethods(self.session, url).request('GET')
        return ParseMethods.parse_config(response)

    def reattach_multi_device_templates(self, template_ids):
        """Re-Attach a template to the devices it it attached to.

        Args:
            template_id (str): The template ID to attach to
            config_type (str): Type of template i.e. device or CLI template
            is_edited (bool): True if the template has been edited
            is_master_edited (bool): For CLI device template needs to match is_edited.
                    For device templates using feature templates needs to be set to False.

        Returns:
            action_id (str): Returns the action id of the attachment

        """

        payload = self.get_multi_attach_payload(template_ids)

        if payload['deviceTemplateList'][0]['device']:
            url = f"{self.base_url}template/device/config/attachfeature"

            utils = Utilities(self.session, self.host, self.port)
            response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
            action_id = ParseMethods.parse_id(response)
            utils.waitfor_action_completion(action_id)
        else:
            raise RuntimeError(f"Could not retrieve input for template {template_ids}")
        return action_id

    def get_multi_attach_payload(self, template_ids):

        return_dict = {"deviceTemplateList": []}
        i = 0
        for template_id in template_ids:
            return_dict['deviceTemplateList'].append({
                "templateId": template_id,
                "device": [],
                "isEdited": True,
                "isMasterEdited": False
            })
            url = f"{self.base_url}template/device/config/attached/{template_id}"
            attach_resp = HttpMethods(self.session, url).request('GET')
            device_list = attach_resp['json']['data']
            for device in device_list:
                payload = {
                    "templateId": template_id,
                    "deviceIds": [device['uuid']],
                    "isEdited": False,
                    "isMasterEdited": False
                }
                url = f"{self.base_url}template/device/config/input"
                input_resp = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
                return_dict['deviceTemplateList'][i]['device'].append(input_resp['json']['data'][0])
            i += 1

        return return_dict
