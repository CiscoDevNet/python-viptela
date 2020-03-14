"""Cisco vManage Device Templates API Methods.
"""

import json
import requests
import re
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.api.feature_templates import FeatureTemplates


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

    # Need to decide where this goes
    def list_to_dict(self, list, key_name, remove_key=True):
        dict = {}
        for item in list:
            if key_name in item:
                if remove_key:
                    key = item.pop(key_name)
                else:
                    key = item[key_name]

                dict[key] = item

        return dict

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
        else:
            return {}

    def get_device_template_list(self, factory_default=False, name_list = []):
        """Get the list of device templates.

        Args:
            factory_default (bool): Include factory default
            name_list (list of strings): A list of template names to retreive.

        Returns:
            result (dict): All data associated with a response.
        """
        device_templates = self.get_device_templates()

        return_list = []
        feature_template_dict = self.feature_templates.get_feature_template_dict(factory_default=True, key_name='templateId')

        for device in device_templates:
            # If there is a list of template name, only return the ones asked for.
            # Otherwise, return them all
            if name_list and device['templateName'] not in name_list:
                continue
            object = self.get_device_template_object(device['templateId'])
            if object:
                if not factory_default and object['factoryDefault']:
                    continue
                if 'generalTemplates' in object:
                    generalTemplates = []
                    for old_template in object.pop('generalTemplates'):
                        new_template = {
                            'templateName': feature_template_dict[old_template['templateId']]['templateName'],
                            'templateType': old_template['templateType']}
                        if 'subTemplates' in old_template:
                            subTemplates = []
                            for sub_template in old_template['subTemplates']:
                                subTemplates.append({'templateName':feature_template_dict[sub_template['templateId']]['templateName'], 'templateType':sub_template['templateType']})
                            new_template['subTemplates'] = subTemplates
                        generalTemplates.append(new_template)
                    object['generalTemplates'] = generalTemplates

                    object['templateId'] = device['templateId']
                    object['attached_devices'] = self.get_template_attachments(device['templateId'])
                    object['input'] = self.get_template_input(device['templateId'])
                    object.pop('templateId')
                    return_list.append(object)

        return return_list

    def get_device_template_dict(self, factory_default=False, key_name='templateName', remove_key=True, name_list = []):
        device_template_list = self.get_device_template_list(factory_default=factory_default, name_list=name_list)

        return self.list_to_dict(device_template_list, key_name, remove_key)

    def get_template_attachments(self, template_id, key='host-name'):
        """Get the devices that a template is attached to.


        Args:
            template_id (string): Template ID
            key (string): The key of the device to put in the list (default: host-name)

        Returns:
            result (list): List of keys.

        """
        api = f"template/device/config/attached/{template_id}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        attached_devices = []
        for device in result:
            attached_devices.append(device[key])

        return attached_devices      

    def get_template_input(self, template_id):
        """Get the input associated with a device attachment.


        Args:
            template_id (string): Template ID

        Returns:
            result (dict): All data associated with a response.

        """        
        payload = {
            "deviceIds": [],
            "isEdited": False,
            "isMasterEdited": False,
            "templateId": template_id
        }
        return_dict = {
            "columns": [],
        }

        api = "template/device/config/input"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))

        if response['json']:
            if 'header' in response['json'] and 'columns' in response['json']['header']:
                column_list = response['json']['header']['columns']

                regex = re.compile(r'\((?P<variable>[^(]+)\)')

                for column in column_list:
                    if column['editable']:
                        match = regex.search(column['title'])
                        if match:
                            variable = match.groups('variable')[0]
                        else:
                            variable = None

                        entry = {'title': column['title'],
                                 'property': column['property'],
                                 'variable': variable}
                        return_dict['columns'].append(entry)

        return return_dict     

    def add_device_template(self, device_template):
        """Add a device template to Vmanage.


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
            api = "template/device/feature"
            url = self.base_url + api
            response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        return response

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
                    'templateType': template['templateType']}
                if 'subTemplates' in template:
                    subTemplates = []
                    for sub_template in template['subTemplates']:
                        if sub_template['templateName'] in feature_templates:
                            subTemplates.append(
                                {'templateId': feature_templates[sub_template['templateName']]['templateId'],
                                 'templateType': sub_template['templateType']})
                        else:
                            self.fail_json(msg="There is no existing feature template named {0}".format(
                                sub_template['templateName']))
                    template_item['subTemplates'] = subTemplates

                converted_generalTemplates.append(template_item)
            else:
                self.fail_json(msg="There is no existing feature template named {0}".format(template['templateName']))

        return converted_generalTemplates   