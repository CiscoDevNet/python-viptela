"""Cisco vManage Device Templates API Methods.
"""

import json
import re
import dictdiffer
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.api.device import Device
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.api.utilities import Utilities
from vmanage.utils import list_to_dict


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
        feature_template_dict = self.feature_templates.get_feature_template_dict(factory_default=True,
                                                                                 key_name='templateId')

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
                if 'generalTemplates' in obj:
                    generalTemplates = []
                    for old_template in obj.pop('generalTemplates'):
                        new_template = {
                            'templateName': feature_template_dict[old_template['templateId']]['templateName'],
                            'templateType': old_template['templateType']
                        }
                        if 'subTemplates' in old_template:
                            subTemplates = []
                            for sub_template in old_template['subTemplates']:
                                subTemplates.append({
                                    'templateName':
                                    feature_template_dict[sub_template['templateId']]['templateName'],
                                    'templateType':
                                    sub_template['templateType']
                                })
                            new_template['subTemplates'] = subTemplates
                        generalTemplates.append(new_template)
                    obj['generalTemplates'] = generalTemplates

                    obj['templateId'] = device['templateId']
                    obj['attached_devices'] = self.get_template_attachments(device['templateId'])
                    obj['input'] = self.get_template_input(device['templateId'])
                    # obj.pop('templateId')
                    return_list.append(obj)

        return return_list

    def get_device_template_dict(self, factory_default=False, key_name='templateName', remove_key=True, name_list=None):
        """Obtain a dictionary of all configured device templates.


        Args:
            factory_default (bool): Wheter to return factory default templates
            key_name (string): The name of the attribute to use as the dictionary key
            remove_key (boolean): remove the search key from the element

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

                regex = re.compile(r'\((?P<variable>[^(]+)\)')

                for column in column_list:
                    if column['editable']:
                        match = regex.search(column['title'])
                        if match:
                            variable = match.groups('variable')[0]
                        else:
                            # If the variable is not found, but is a default entry
                            variable = None

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
            'policyId': '',
            'featureTemplateUidRange': []
        }
        #
        # File templates are much easier in that they are just a bunch of CLI
        #
        if device_template['configType'] == 'file':
            payload['templateConfiguration'] = device_template['templateConfiguration']
            api = "template/device/cli"
            url = self.base_url + api
            response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        #
        # Feature based templates are just a list of templates Id that make up a devie template.  We are
        # given the name of the feature templates, but we need to translate that to the template ID
        #
        else:
            if 'generalTemplates' in device_template:
                payload['generalTemplates'] = self.generalTemplates_to_id(device_template['generalTemplates'])
            else:
                raise Exception("No generalTemplates found in device template", data=device_template)
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
        if device_template['configType'] == 'file':
            url = f"{self.base_url}template/device/cli/{device_template['templateId']}"
            response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(device_template))
        #
        # Feature based templates are just a list of templates Id that make up a devie template.  We are
        # given the name of the feature templates, but we need to translate that to the template ID
        #
        else:
            if 'generalTemplates' in device_template:
                device_template['generalTemplates'] = self.generalTemplates_to_id(device_template['generalTemplates'])
            else:
                raise Exception("No generalTemplates found in device template", data=device_template)
            url = f"{self.base_url}template/device/feature/{device_template['templateId']}"
            response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(device_template))
        return response

    def import_device_template_list(self, device_template_list, check_mode=False, update=False):
        """Import a list of feature templates to vManage.


        Args:
            check_mode (bool): Only check to see if changes would be made
            update (bool): Update the template if it exists

        Returns:
            result (list): Returns the diffs of the updates.

        """
        device_template_updates = []
        device_template_dict = self.get_device_template_dict()
        for device_template in device_template_list:
            if device_template['templateName'] in device_template_dict:
                existing_template = device_template_dict[device_template['templateName']]
                if 'generalTemplates' in device_template:
                    diff = list(
                        dictdiffer.diff(existing_template['generalTemplates'], device_template['generalTemplates']))
                elif 'templateConfiguration' in device_template:
                    diff = list(
                        dictdiffer.diff(existing_template['templateConfiguration'],
                                        device_template['templateConfiguration']))
                else:
                    raise Exception("Template {0} is of unknown type".format(device_template['templateName']))
                if len(diff):
                    device_template_updates.append({'name': device_template['templateName'], 'diff': diff})
                    if not check_mode and update:
                        self.update_device_template(device_template)
            else:
                if 'generalTemplates' in device_template:
                    diff = list(dictdiffer.diff({}, device_template['generalTemplates']))
                elif 'templateConfiguration' in device_template:
                    diff = list(dictdiffer.diff({}, device_template['templateConfiguration']))
                else:
                    raise Exception("Template {0} is of unknown type".format(device_template['templateName']))
                device_template_updates.append({'name': device_template['templateName'], 'diff': diff})
                if not check_mode:
                    self.add_device_template(device_template)

        return device_template_updates

    def import_attachment_list(self, attachment_list, check_mode=False, update=False):
        """Import a list of device attachments to vManage.


        Args:
            check_mode (bool): Only check to see if changes would be made
            update (bool): Update the template if it exists

        Returns:
            result (list): Returns the diffs of the updates.

        """
        attachment_updates = {}
        attachment_failures = {}
        action_id_list = []
        device_template_dict = self.get_device_template_dict()
        vmanage_device = Device(self.session, self.host, self.port)
        for attachment in attachment_list:
            if attachment['template'] in device_template_dict:
                if attachment['device_type'] == 'vedge':
                    # The UUID is fixes from the serial file/upload
                    device_uuid = attachment['uuid']
                else:
                    # If this is not a vedge, we need to get the UUID from the vmanage since
                    # it is generated by that vmanage
                    device_status = vmanage_device.get_device_status(attachment['host_name'], key='host-name')
                    if device_status:
                        device_uuid = device_status['uuid']
                    else:
                        raise Exception(f"Cannot find UUID for {attachment['host_name']}")

                template_id = device_template_dict[attachment['template']]['templateId']
                attached_uuid_list = self.get_attachments(template_id, key='uuid')
                if device_uuid in attached_uuid_list:
                    # The device is already attached to the template.  We need to see if any of
                    # the input changed, so we make an API call to get the input on last attach
                    existing_template_input = self.get_template_input(
                        device_template_dict[attachment['template']]['templateId'], [device_uuid])
                    current_variables = existing_template_input['data'][0]
                    changed = False
                    for property_name in attachment['variables']:
                        # Check to see if any of the passed in varibles have changed from what is
                        # already on the attachment.  We are are not checking to see if the
                        # correct variables are here.  That will be done on attachment.
                        if ((property_name in current_variables) and
                            (str(attachment['variables'][property_name]) != str(current_variables[property_name]))):
                            changed = True
                    if changed:
                        action_id_list.append(action_id)
                        if not check_mode:
                            action_id = self.attach_to_template(template_id, device_uuid, attachment['system_ip'],
                                                                attachment['host_name'], attachment['site_id'],
                                                                attachment['variables'])
                else:
                    action_id_list.append(action_id)
                    if not check_mode and update:
                        action_id = self.attach_to_template(template_id, device_uuid, attachment['system_ip'],
                                                            attachment['host_name'], attachment['site_id'],
                                                            attachment['variables'])
            else:
                raise Exception(f"No template named Template {attachment['templateName']}")

        # pp = pprint.PrettyPrinter(indent=2)
        utilities = Utilities(self.session, self.host)
        # Batch the waits so that the peocessing of the attachments is in parallel
        for action_id in action_id_list:
            result = utilities.waitfor_action_completion(action_id)
            data = result['action_response']['data'][0]
            # pp.pprint(data)
            if result['action_status'] == 'failure':
                attachment_failures.update({data['uuid']: data['currentActivity']})
            else:
                attachment_updates.update({data['uuid']: data['currentActivity']})

        result = {'updates': attachment_updates, 'failures': attachment_failures}
        return result

    def attach_to_template(self, template_id, uuid, system_ip, host_name, site_id, variables):
        """Attach and device to a template

        Args:
            template_id (str): The template ID to attach to
            uuid (str): The UUID of the device to attach
            system_ip (str): The System IP of the system to attach
            host_name (str): The host-name of the device to attach
            variables (dict): The variables needed by the template

        Returns:
            action_id (str): Returns the action id of the attachment

        """
        # Construct the variable payload
        device_template_variables = {
            "csv-status": "complete",
            "csv-deviceId": uuid,
            "csv-deviceIP": system_ip,
            "csv-host-name": host_name,
            '//system/host-name': host_name,
            '//system/system-ip': system_ip,
            '//system/site-id': site_id,
        }
        # Make sure they passed in the required variables and map
        # variable name -> property mapping
        template_variables = self.get_template_input(template_id)
        for entry in template_variables['columns']:
            if entry['variable']:
                if entry['variable'] in variables:
                    device_template_variables[entry['property']] = variables[entry['variable']]
                else:
                    raise Exception(f"{entry['variable']} is missing for {host_name}")

        payload = {
            "deviceTemplateList": [{
                "templateId": template_id,
                "device": [device_template_variables],
                "isEdited": False,
                "isMasterEdited": False
            }]
        }
        url = f"{self.base_url}template/device/config/attachfeature"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        if 'json' in response and 'id' in response['json']:
            action_id = response['json']['id']
        else:
            raise Exception('Did not get action ID after attaching device to template.')

        return action_id

    def detach_from_template(self, uuid, device_ip, device_type):
        """Detach a device from a template (i.e. Put in CLI mode)

        Args:
            uuid (str): The UUID of the device to detach
            system_ip (str): The System IP of the system to detach
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
        ParseMethods.parse_data(response)

        if 'json' in response and 'id' in response['json']:
            action_id = response.json['id']
        else:
            raise Exception('Did not get action ID after attaching device to template.')
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

    def generalTemplates_to_id(self, generalTemplates):
        converted_generalTemplates = []
        feature_templates = self.feature_templates.get_feature_template_dict(factory_default=True)
        for template in generalTemplates:
            if 'templateName' not in template:
                self.result['generalTemplates'] = generalTemplates
                self.fail_json(msg="Bad template")
            if template['templateName'] in feature_templates:
                template_item = {
                    'templateId': feature_templates[template['templateName']]['templateId'],
                    'templateType': template['templateType']
                }
                if 'subTemplates' in template:
                    subTemplates = []
                    for sub_template in template['subTemplates']:
                        if sub_template['templateName'] in feature_templates:
                            subTemplates.append({
                                'templateId':
                                feature_templates[sub_template['templateName']]['templateId'],
                                'templateType':
                                sub_template['templateType']
                            })
                        else:
                            self.fail_json(msg="There is no existing feature template named {0}".format(
                                sub_template['templateName']))
                    template_item['subTemplates'] = subTemplates

                converted_generalTemplates.append(template_item)
            else:
                self.fail_json(msg="There is no existing feature template named {0}".format(template['templateName']))

        return converted_generalTemplates
