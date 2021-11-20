"""Cisco vManage Feature Templates API Methods.
"""

import json

from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


class FeatureTemplates(object):
    """vManage Feature Templates API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Feature Templates.

    """
    def __init__(self, session, host, port=443):
        """Initialize Feature Templates object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def delete_feature_template(self, templateId):
        """Obtain a list of all configured feature templates.

        Args:
            templateId (str): Object ID for feature template

        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/feature/{templateId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

    def get_feature_templates(self):
        """Obtain a list of all configured feature templates.

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/feature"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def add_feature_template(self, feature_template):
        """Add a feature template to Vmanage.


        Args:
            feature_template (dict): Feature Template

        Returns:
            result (list): Response from Vmanage

        """
        payload = {
            'templateName': feature_template['templateName'],
            'templateDescription': feature_template['templateDescription'],
            'deviceType': feature_template['deviceType'],
            'templateDefinition': feature_template['templateDefinition'],
            'templateType': feature_template['templateType'],
            'templateMinVersion': feature_template['templateMinVersion'],
            'factoryDefault': feature_template['factoryDefault'],
            'configType': feature_template['configType'],
            # 'feature': feature_template['feature'],
        }
        api = "template/feature"
        url = self.base_url + api
        return HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))

    def update_feature_template(self, feature_template):
        """Update a feature template on Vmanage.


        Args:
            feature_template (dict): Feature Template

        Returns:
            result (list): Response from Vmanage

        """
        url = f"{self.base_url}template/feature/{feature_template['templateId']}"
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(feature_template))
        return response

    def get_feature_template_list(self, factory_default=False, name_list=None):
        """Obtain a list of all configured feature templates.


        Args:
            factory_default (bool): Whether to return factory default templates
            name_list (list of strings): A list of the template names to return

        Returns:
            result (dict): All data associated with a response.

        """
        if name_list is None:
            name_list = []
        feature_templates = self.get_feature_templates()

        return_list = []
        for template in feature_templates:
            if not factory_default and template['factoryDefault']:
                continue
            if name_list and template['templateName'] not in name_list:
                continue
            template['templateDefinition'] = json.loads(template['templateDefinition'])
            template.pop('editedTemplateDefinition', None)
            return_list.append(template)

        return return_list

    def get_feature_template_dict(self,
                                  factory_default=False,
                                  key_name='templateName',
                                  remove_key=True,
                                  name_list=None):
        """Obtain a dictionary of all configured feature templates.


        Args:
            factory_default (bool): Whether to return factory default templates
            key_name (string): The name of the attribute to use as the dictionary key
            remove_key (boolean): Remove the search key from the element
            name_list (list of strings): A list of the template names to return

        Returns:
            result (dict): All data associated with a response.

        """
        if name_list is None:
            name_list = []
        feature_template_list = self.get_feature_template_list(factory_default=factory_default, name_list=name_list)

        return list_to_dict(feature_template_list, key_name, remove_key)

    def get_device_templates_for_feature(self, templateId):
        """Obtain a list of device templates for given feature template


        Args:
           templateId: (str)  Feature template ID to find device templates for

        Returns:
            result (dict): All data associated with a response.

        """
        url = f"{self.base_url}template/feature/devicetemplates/{templateId}"
        response = HttpMethods(self.session, url).request('GET')
        return ParseMethods.parse_data(response)
