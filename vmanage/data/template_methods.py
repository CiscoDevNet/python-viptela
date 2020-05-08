"""Cisco vManage Templates Methods.
"""

import dictdiffer
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.local_policy import LocalPolicy


class TemplateMethods(object):
    """vManage Device Methods

    Responsible vManage Device Templates.

    """
    def __init__(self, session, host, port=443):
        """Initialize Templates Method object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.device_templates = DeviceTemplates(self.session, self.host, self.port)
        self.feature_templates = FeatureTemplates(self.session, self.host, self.port)

    def convert_device_template_to_name(self, device_template):
        """Convert a device template components from IDs to Names.

        Args:
            device_template (dict): Device Template

        Returns:
            result (dict): Converted Device Template.
        """

        feature_template_dict = self.feature_templates.get_feature_template_dict(factory_default=True,
                                                                                 key_name='templateId')

        if 'policyId' in device_template and device_template['policyId']:
            policy_id = device_template['policyId']
            vmanage_local_policy = LocalPolicy(self.session, self.host, self.port)
            local_policy_dict = vmanage_local_policy.get_local_policy_dict(key_name='policyId')
            if policy_id in list(local_policy_dict.keys()):
                device_template['policyName'] = local_policy_dict[policy_id]['policyName']
            else:
                raise Exception(f"Could not find local policy {policy_id}")

        if 'generalTemplates' in device_template:
            generalTemplates = []
            for old_template in device_template.pop('generalTemplates'):
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
            device_template['generalTemplates'] = generalTemplates

        return device_template

    def convert_device_template_to_id(self, device_template):
        """Convert a device template components from Names to IDs.

        Args:
            device_template (dict): Device Template

        Returns:
            result (dict): Converted Device Template.
        """

        if 'PolicyName' in device_template:
            vmanage_local_policy = LocalPolicy(self.session, self.host, self.port)
            local_policy_dict = vmanage_local_policy.get_local_policy_dict(key_name='policyId')
            if device_template['PolicyName'] in local_policy_dict:
                device_template['PolicyId'] = local_policy_dict[device_template['PolicyName']]['PolicyId']
                device_template.pop('PolicyName')
            else:
                raise Exception(f"Could not find local policy {device_template['PolicyName']}")

        if 'generalTemplates' in device_template:
            device_template['generalTemplates'] = self.generalTemplates_to_id(device_template['generalTemplates'])

        return device_template

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

    def import_device_template_list(self, device_template_list, check_mode=False, update=False):
        """Add a list of feature templates to vManage.


        Args:
            check_mode (bool): Only check to see if changes would be made
            update (bool): Update the template if it exists

        Returns:
            result (list): Returns the diffs of the updates.

        """
        device_template_updates = []
        device_template_dict = self.device_templates.get_device_template_dict()
        for device_template in device_template_list:
            if device_template['templateName'] in device_template_dict:
                existing_template = self.convert_device_template_to_name(
                    device_template_dict[device_template['templateName']])
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
                        if not check_mode:
                            converted_device_template = self.convert_device_template_to_id(device_template)
                            self.update_device_template(converted_device_template)
            else:
                if 'generalTemplates' in device_template:
                    diff = list(dictdiffer.diff({}, device_template['generalTemplates']))
                elif 'templateConfiguration' in device_template:
                    diff = list(dictdiffer.diff({}, device_template['templateConfiguration']))
                else:
                    raise Exception("Template {0} is of unknown type".format(device_template['templateName']))
                device_template_updates.append({'name': device_template['templateName'], 'diff': diff})
                if not check_mode:
                    converted_device_template = self.convert_device_template_to_id(device_template)
                    self.add_device_template(converted_device_template)

        return device_template_updates
