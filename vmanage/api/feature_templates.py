"""Cisco vManage Feature Templates API Methods.
"""

import json

import dictdiffer
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
        """Add a feature template to Vmanage.


        Args:
            feature_template (dict): Feature Template

        Returns:
            result (list): Response from Vmanage

        """
        url = f"{self.base_url}template/feature/{feature_template['templateId']}"
        return HttpMethods(self.session, url).request('PUT', payload=json.dumps(feature_template))

    def get_feature_template_list(self, factory_default=False, name_list=None):
        """Obtain a list of all configured feature templates.


        Args:
            factory_default (bool): Wheter to return factory default templates
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
            factory_default (bool): Wheter to return factory default templates
            key_name (string): The name of the attribute to use as the dictionary key
            remove_key (boolean): remove the search key from the element

        Returns:
            result (dict): All data associated with a response.

        """
        if name_list is None:
            name_list = []
        feature_template_list = self.get_feature_template_list(factory_default=factory_default, name_list=name_list)

        return list_to_dict(feature_template_list, key_name, remove_key)

    def import_feature_template_list(self, feature_template_list, check_mode=False, update=False):
        """Add a list of feature templates to vManage.


        Args:
            check_mode (bool): Only check to see if changes would be made
            update (bool): Update the template if it exists

        Returns:
            result (list): Returns the diffs of the updates.

        """
        # Process the feature templates
        feature_template_updates = []
        feature_template_dict = self.get_feature_template_dict(factory_default=True, remove_key=False)
        for feature_template in feature_template_list:
            if feature_template['templateName'] in feature_template_dict:
                existing_template = feature_template_dict[feature_template['templateName']]
                feature_template['templateId'] = existing_template['templateId']
                diff = list(
                    dictdiffer.diff(existing_template['templateDefinition'], feature_template['templateDefinition']))
                if len(diff):
                    feature_template_updates.append({'name': feature_template['templateName'], 'diff': diff})
                    if not check_mode and update:
                        self.update_feature_template(feature_template)
            else:
                diff = list(dictdiffer.diff({}, feature_template['templateDefinition']))
                feature_template_updates.append({'name': feature_template['templateName'], 'diff': diff})
                if not check_mode:
                    self.add_feature_template(feature_template)

        return feature_template_updates
