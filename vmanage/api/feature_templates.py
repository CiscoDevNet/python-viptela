"""Cisco vManage Feature Templates API Methods.

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
from vmanage.data.parse_methods import ParseMethods


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
        return(result)

    def get_feature_templates(self):
        """Obtain a list of all configured feature templates.

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/feature"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return(result)

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

    def get_feature_template_list(self, factory_default=False, name_list = []):
        """Obtain a list of all configured feature templates.


        Args:
            factory_default (bool): Wheter to return factory default templates
            name_list (list of strings): A list of the template names to return

        Returns:
            result (dict): All data associated with a response.

        """

        api = "template/feature"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        return_list = []
        for template in result:
            if not factory_default and template['factoryDefault']:
                continue
            if name_list and template['templateName'] not in name_list:
                continue
            template['templateDefinition'] = json.loads(template['templateDefinition'])
            template.pop('editedTemplateDefinition', None)
            return_list.append(template)

        return return_list

    def get_feature_template_dict(self, factory_default=False, key_name='templateName', remove_key=True, name_list = []):
        feature_template_list = self.get_feature_template_list(factory_default=factory_default, name_list=name_list)

        return self.list_to_dict(feature_template_list, key_name, remove_key)