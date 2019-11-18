from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import requests
import re
import time
import os
import urllib3
import dictdiffer
import yaml
import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# from requests.exceptions import ConnectionError

# from . import constants, exceptions, utils


STANDARD_HTTP_TIMEOUT = 10
STANDARD_JSON_HEADER = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}
POLICY_LIST_DICT = {
    'siteLists': 'site',
    'vpnLists': 'vpn',
}
POLICY_DEFINITION_TYPES = ['cflowd', 'dnssecurity', 'control', 'hubandspoke', 'acl', 'vpnmembershipgroup',
                                        'mesh', 'rewriterule', 'data', 'rewriterule', 'aclv6']
POLICY_LIST_TYPES = ['community', 'localdomain', 'ipv6prefix', 'dataipv6prefix', 'tloc', 'aspath', 'zone',
                                  'color', 'sla', 'app', 'mirror', 'dataprefix', 'extcommunity', 'site', 'ipprefixall',
                                  'prefix', 'umbrelladata', 'class', 'ipssignature', 'dataprefixall',
                                  'urlblacklist', 'policer', 'urlwhitelist', 'vpn']                                      
VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]

class vmanage_session(object):

    def __init__(self, host=None, user=None, password=None, port=8443,
                validate_certs=False, disable_warnings=False, timeout=10):
        self.headers = dict()
        self.cookies = None
        self.json = None

        self.method = None
        self.path = None
        self.response = None
        self.status = None
        self.url = None
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.timeout = os.getenv('VMANAGE_TIMEOUT', timeout)
        self.base_url = 'https://{0}:{1}/dataservice'.format(self.host, self.port)
        self.session = requests.Session()
        self.session.verify = validate_certs
        self.policy_list_cache = {}
        self.login()


    def login(self):
        try:
            response = self.session.post(
                url='{0}/j_security_check'.format(self.base_url),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'j_username': self.user, 'j_password': self.password},
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:
            raise Exception('Could not connect to {0}: {1}'.format(self.host, e))

        if response.status_code != 200 or response.text.startswith('<html>'):
            raise Exception('Could not login to device, check user credentials.')

        response = self.session.get(
            url='https://{0}/dataservice/client/token'.format(self.host),
            timeout=self.timeout
        )
        if response.status_code == 200:
            self.session.headers['X-XSRF-TOKEN'] = response.content
        elif response.status_code == 404:
            # Assume this is pre-19.2
            pass
        else:
            raise Exception('Failed getting X-XSRF-TOKEN: {0}'.format(response.status_code))

    def request(self, url_path, method='GET', headers=STANDARD_JSON_HEADER, data=None, files=None, payload=None, status_codes=VALID_STATUS_CODES):
        """Generic HTTP method for viptela requests."""
        url = '{0}{1}'.format(self.base_url, url_path)
        if payload:
            data = json.dumps(payload)

        error = None
        details = None
        try:
            response = self.session.request(method, url, headers=headers, files=files, data=data)
        except requests.RequestException as e:
            if e.response is not None:
                details = e.response
                error = [e.response.json()['errorMessage']]
            else:
                error = [(str(e))]

        try:
            result_json = response.json()
        except:
            if response.text:
                result_json = json.loads(response.text)
            else:
                result_json = {}

        if response.status_code not in status_codes:
            if 'error' in result_json:
                error='Unknown'
                details='Unknown'
                if 'details' in result_json['error']:
                    details = result_json['error']['details']
                if 'message' in result_json['error']:
                    error = result_json['error']['message']
                raise Exception('{0}: {1}'.format(error, details))
            else:
                raise Exception(f"{url}: Error {response.status_code}")

        result = {
            'status_code': response.status_code,
            'status': requests.status_codes._codes[response.status_code][0],
            'details': details,
            'error': error,
            'json': result_json,
            'response': response,
        }
        return result

    def list_to_dict(self, list, key_name, remove_key=True):
        dict = {}
        for item in list:
            if key_name in item:
                if remove_key:
                    key = item.pop(key_name)
                else:
                    key = item[key_name]

                dict[key] = item
            # else:
            #     self.fail_json(msg="key {0} not found in dictionary".format(key_name))

        return dict

#
# Devices
#
    def get_device_status_list(self):
        result = self.request('/device')

        try:
            return result['json']['data']
        except:
            return []

    def get_device_status_dict(self, key_name='host-name', remove_key=False):

        device_list = self.get_device_status_list()

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

    def get_device_status(self, value, key='system-ip'):
        result = self.request('/device?{0}={1}'.format(key, value))

        try:
            return result['json']['data'][0]
        except:
            return {}

    def get_device_list(self):
        result = self.request('/device')

        try:
            return result['json']['data']
        except:
            return []

    def get_device_dict(self, key_name='host-name', remove_key=False):

        device_list = self.get_device_list()

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

    def get_device_by_device_ip(self, device_ip):
        result = self.request('/system/device/controllers?deviceIP={0}'.format(device_ip))        
        if 'data' in result['json'] and result['json']['data']:
            return result['json']['data']
        
        result = self.request('/system/device/vedges?deviceIP={0}'.format(device_ip))

        try:
            return result['json']['data']
        except:
            return {}

    def get_device_config(self, type, device_ip):
        result = self.request('/system/device/{0}?deviceIP={1}'.format(type, device_ip))        

        try:
            return result['json']['data'][0]
        except:
            return {}

    def get_device_config_list(self, type):
        result = self.request('/system/device/{0}'.format(type))

        try:
            return result['json']['data']
        except:
            return []

    def get_device_config_dict(self, type, key_name='host-name', remove_key=False):

        device_list = self.get_device_config_list(type)

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

#
# Templates
#

    def get_device_template_list(self, factory_default=False, name_list = []):
        result = self.request('/template/device')

        return_list = []
        if 'data' in result['json']:
            device_body = result['json']
            feature_template_dict = self.get_feature_template_dict(factory_default=True, key_name='templateId')
            for device in device_body['data']:
                if name_list and device['templateName'] not in name_list:
                    continue
                object_result = self.request('/template/device/object/{0}'.format(device['templateId']))
                if object_result['json']:
                    object = object_result['json']
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

    def get_feature_template_list(self, factory_default=False, name_list = []):
        result = self.request('/template/feature')

        return_list = []
        if 'json' in result:
            template_list = result['json']['data']
            for template in template_list:
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

    def get_template_attachments(self, template_id, key='host-name'):
        result = self.request('/template/device/config/attached/{0}'.format(template_id))

        attached_devices = []
        if 'json' in result:
            device_list = result['json']['data']
            for device in device_list:
                attached_devices.append(device[key])

        return attached_devices      

    def get_template_input(self, template_id):
        payload = {
            "deviceIds": [],
            "isEdited": False,
            "isMasterEdited": False,
            "templateId": template_id
        }
        return_dict = {
            "columns": [],
        }
        result = self.request('/template/device/config/input', method='POST', payload=payload)

        if result['json']:
            if 'header' in result['json'] and 'columns' in result['json']['header']:
                column_list = result['json']['header']['columns']

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
    def export_templates_to_file(self, export_file, name_list = [], type = None):
        template_export = {}
        if type != 'feature':
            # Export the device templates and associated feature templates
            device_template_list = self.get_device_template_list(name_list=name_list)
            template_export.update({'vmanage_device_templates': device_template_list})
            feature_name_list = []
            if name_list:
                for device_template in device_template_list:
                    if 'generalTemplates' in device_template:
                        for general_template in device_template['generalTemplates']:
                            if 'templateName' in general_template:
                                feature_name_list.append(general_template['templateName'])
                            if 'subTemplates' in general_template:
                                for sub_template in general_template['subTemplates']:
                                    if 'templateName' in sub_template:
                                        feature_name_list.append(sub_template['templateName'])
                name_list = list(set(feature_name_list))
        # Since device templates depend on feature templates, we always add them.
        feature_template_list = self.get_feature_template_list(name_list=name_list)
        template_export.update({'vmanage_feature_templates': feature_template_list})


        if export_file.endswith('.json'):
            with open(export_file, 'w') as outfile:
                json.dump(template_export, outfile, indent=4, sort_keys=False)
        elif export_file.endswith('.yaml') or export_file.endswith('.yml'):
            with open(export_file, 'w') as outfile:
                yaml.dump(template_export, outfile, indent=4, sort_keys=False)
        else:
            raise Exception("File format not supported")    

    def import_templates_from_file(self, file, update=False, check_mode=False, name_list = [], type = None):
        changed = False
        feature_template_updates = []
        device_template_updates = []
        template_data = {}
        feature_template_data = {}

        # Read in the datafile
        if not os.path.exists(file):
            raise Exception(msg='Cannot find file {0}'.format(file))
        with open(file) as f:
            if file.endswith('.yaml') or file.endswith('.yml'):
                template_data = yaml.safe_load(f)
            else:
                template_data = json.load(f)

        if 'vmanage_feature_templates' in template_data:
            imported_feature_template_list = template_data['vmanage_feature_templates']
        else:
            imported_feature_template_list = []

        imported_device_template_list = []

        if type != 'feature':
            # Import the device templates and associated feature templates
            if 'vmanage_device_templates' in template_data:
                imported_device_template_list = template_data['vmanage_device_templates']
            if name_list:
                feature_name_list = []
                pruned_device_template_list = []
                for device_template in imported_device_template_list:
                    if device_template['templateName'] in name_list:
                        pruned_device_template_list.append(device_template)
                        if 'generalTemplates' in device_template:
                            for general_template in device_template['generalTemplates']:
                                if 'templateName' in general_template:
                                    feature_name_list.append(general_template['templateName'])
                                if 'subTemplates' in general_template:
                                    for sub_template in general_template['subTemplates']:
                                        if 'templateName' in sub_template:
                                            feature_name_list.append(sub_template['templateName'])
                imported_device_template_list = pruned_device_template_list
                name_list = list(set(feature_name_list))
        # Since device templates depend on feature templates, we always add them.
        if name_list:
            pruned_feature_template_list = []
            imported_feature_template_dict = self.list_to_dict(imported_feature_template_list, key_name='templateName', remove_key=False)
            for feature_template_name in name_list:
                if feature_template_name in imported_feature_template_dict:
                    pruned_feature_template_list.append(imported_feature_template_dict[feature_template_name])
                # Otherwise, we hope the feature list is already there (e.g. Factory Default)
            imported_feature_template_list = pruned_feature_template_list

        # Process the feature templates
        feature_template_dict = self.get_feature_template_dict(factory_default=True, remove_key=False)
        for feature_template in imported_feature_template_list:
            if feature_template['templateName'] in feature_template_dict:
                existing_template = feature_template_dict[feature_template['templateName']]
                diff = list(dictdiffer.diff(existing_template['templateDefinition'], feature_template['templateDefinition']))
                if len(diff):
                    feature_template_updates.append({'name': feature_template['templateName'], 'diff': diff})
                    if not check_mode and update:
                        if not check_mode:
                            self.add_feature_template(feature_template)
            else:
                diff = list(dictdiffer.diff({}, feature_template['templateDefinition']))
                feature_template_updates.append({'name': feature_template['templateName'], 'diff': diff})
                if not check_mode:
                    self.add_feature_template(feature_template)                

        # Process the device templates
        device_template_dict = self.get_device_template_dict()
        for device_template in imported_device_template_list:
            if device_template['templateName'] in device_template_dict:
                existing_template = device_template_dict[device_template['templateName']]
                if 'generalTemplates' in device_template:
                    diff = list(dictdiffer.diff(existing_template['generalTemplates'], device_template['generalTemplates']))
                elif 'templateConfiguration' in device_template:
                    diff = list(dictdiffer.diff(existing_template['templateConfiguration'], device_template['templateConfiguration']))
                else:
                    raise Exception("Template {0} is of unknown type".format(device_template['templateName']))
                if len(diff):
                    device_template_updates.append({'name': device_template['templateName'], 'diff': diff})
                    if not check_mode and update:
                        if not check_mode:
                            self.add_device_template(device_template)
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

        return {
                'feature_template_updates': feature_template_updates,
                'device_template_updates': device_template_updates,
                }        

    def add_feature_template(self, feature_template):
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
        return self.request('/template/feature/', method='POST', data=json.dumps(payload))

    def add_device_template(self, device_template):
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
            self.request('/template/device/cli', method='POST', payload=payload)
        #
        # Feature based templates are just a list of templates Id that make up a devie template.  We are
        # given the name of the feature templates, but we need to translate that to the template ID
        #
        else:
            if 'generalTemplates' in device_template:
                payload['generalTemplates'] = self.generalTemplates_to_id(device_template['generalTemplates'])
            else:
                raise Exception("No generalTemplates found in device template", data=device_template)
            result = self.request('/template/device/feature', method='POST', payload=payload)

    def generalTemplates_to_id(self, generalTemplates):
        converted_generalTemplates = []
        feature_templates = self.get_feature_template_dict(factory_default=True)
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
#
# Policy
#
    # def get_policy_list(self, type, list_id):
    #     result = self.request('/template/policy/list/{0}/{1}'.format(type.lower(), list_id))
    #     return result['json']

    def clear_policy_list_cache(self):
        self.policy_list_cache = {}

    def get_policy_list_list(self, type='all', cache=True):
        # print("Get list {0}". format(type))
        if cache and type in self.policy_list_cache:
            result = self.policy_list_cache[type]
        else:
            if type == 'all':
                result = self.request('/template/policy/list', status_codes=[200])
            else:
                result = self.request('/template/policy/list/{0}'.format(type.lower()), status_codes=[200, 404])

        if result['status_code'] == 404:
            return []
        else:
            self.policy_list_cache[type] = result
            return result['json']['data']

    def get_policy_list_dict(self, type='all', key_name='name', remove_key=False, cache=True):

        policy_list = self.get_policy_list_list(type, cache=cache)

        return self.list_to_dict(policy_list, key_name, remove_key=remove_key)

    def convert_list_id_to_name(self, input):
        if isinstance(input, dict):
            for key, value in list(input.items()):
                if key.endswith('List'):
                    type = key[0:len(key)-4]
                    policy_list_dict = self.get_policy_list_dict(type, key_name='listId')
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['name']
                elif key.endswith('Lists'):
                    type = key[0:len(key)-5]
                    policy_list_dict = self.get_policy_list_dict(type, key_name='listId')
                    new_list = []
                    for list_id in value:
                        if list_id in policy_list_dict:
                            list_name = policy_list_dict[list_id]['name']
                            new_list.append(list_name)
                        else:
                            new_list.append(list_id)
                    input[key] = new_list
                elif key.endswith('Zone'):
                    policy_list_dict = self.get_policy_list_dict('zone', key_name='listId')
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['name']
                elif key == 'ref':
                    policy_list_dict = self.get_policy_list_dict('all', key_name='listId')
                    if input['ref'] in policy_list_dict:
                        input['listName'] = policy_list_dict[input['ref']]['name']
                        input['listType'] = policy_list_dict[input['ref']]['type']
                        input.pop('ref')   
                    else:
                        raise Exception("Could not find list {0}".format(input['ref']))
                elif key == 'class':
                    policy_list_dict = self.get_policy_list_dict('all', key_name='listId')
                    if input['class'] in policy_list_dict:
                        input['className'] = policy_list_dict[input['class']]['name']
                        input['classType'] = policy_list_dict[input['class']]['type']
                        input.pop('class')   
                    else:
                        raise Exception("Could not find list {0}".format(input['ref']))                    
                else:
                    self.convert_list_id_to_name(value)
        elif isinstance(input, list):
            for item in input:
                self.convert_list_id_to_name(item)

    def convert_list_name_to_id(self, input):
        if isinstance(input, dict):
            for key, value in list(input.items()):
                if key.endswith('List'):
                    type = key[0:len(key)-4]
                    policy_list_dict = self.get_policy_list_dict(type)
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['listId']
                elif key.endswith('Lists'):
                    type = key[0:len(key)-5]
                    policy_list_dict = self.get_policy_list_dict(type)
                    new_list = []
                    for list_name in value:
                        if list_name in policy_list_dict:
                            list_id = policy_list_dict[list_name]['listId']
                            new_list.append(list_id)
                        else:
                            new_list.append(list_name)
                    input[key] = new_list
                elif key.endswith('Zone'):
                    policy_list_dict = self.get_policy_list_dict('zone')
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['listId']
                elif key == 'listName':
                    # print(input['listName'])
                    if 'listType' in input:
                        policy_list_dict = self.get_policy_list_dict(input['listType'], key_name='name')
                    else:
                        raise Exception("Could not find type for list {0}".format(input['listName']))
                    if input['listName'] in policy_list_dict and 'listId' in policy_list_dict[input['listName']]:
                        input['ref'] = policy_list_dict[input['listName']]['listId']
                        input.pop('listName')
                        input.pop('listType') 
                    else:
                        raise Exception("Could not find id for list {0}, type {1}".format(input['listName'], input['listType']))
                elif key == 'className':
                    if 'classType' in input:
                        policy_list_dict = self.get_policy_list_dict(input['classType'], key_name='name')
                    else:
                        raise Exception("Could not find type for list {0}".format(input['className']))
                    if input['className'] in policy_list_dict and 'listId' in policy_list_dict[input['className']]:
                        input['class'] = policy_list_dict[input['className']]['listId']
                        input.pop('className')
                        input.pop('classType') 
                    else:
                        raise Exception("Could not find id for list {0}, type {1}".format(input['listName'], input['listType']))                                              
                else:
                    self.convert_list_name_to_id(value)
        elif isinstance(input, list):
            for item in input:
                self.convert_list_name_to_id(item)

    def get_policy_definition(self, definition_type, definition_id):
        result = self.request('/template/policy/definition/{0}/{1}'.format(definition_type.lower(), definition_id))

        if 'json' in result:
            policy_definition = result['json']
            if 'definition' in policy_definition:
                self.convert_list_id_to_name(policy_definition['definition'])
            if 'sequences' in policy_definition:
                self.convert_list_id_to_name(policy_definition['sequences'])
            if 'rules' in policy_definition:
                self.convert_list_id_to_name(policy_definition['rules'])                    
            return policy_definition
        else:
            return {}

    def get_policy_definition_list(self, definition_type='all'):
        if definition_type == 'all':
            # policy_list_dict = self.get_policy_list_dict('all', key_name='listId')
            # Get a list of hub-and-spoke because it tells us the other definition types
            # known by this server (hopefully)
            all_definitions_list = []
            definition_list_types = []
            result = self.request('/template/policy/definition/hubandspoke')
            try:
                definition_type_titles = result['json']['header']['columns'][1]['keyvalue']
            except:
                raise Exception('Could not retrieve definition types')
            for definition_type in definition_type_titles:
                definition_list_types.append(definition_type['key'].lower())

            for definition_type in definition_list_types:
                definition_list = self.get_policy_definition_list(definition_type)
                if definition_list:
                    all_definitions_list.extend(definition_list)
            return all_definitions_list
        else:
            definition_list = []
            policy_list_dict = self.get_policy_list_dict('all', key_name='listId')
            result = self.request('/template/policy/definition/{0}'.format(definition_type.lower()))
            if 'data' in result['json']:
                for definition in result['json']['data']:
                    definition_detail = self.get_policy_definition(definition_type, definition['definitionId'])
                    if definition_detail:
                        # if 'sequences' in definition_detail:
                        #     for sequence in definition_detail['sequences']:
                        #         if 'match' in sequence and 'entries' in sequence['match']:
                        #             for entry in sequence['match']['entries']:
                        #                 if 'ref' in entry and entry['ref'] in policy_list_dict:
                        #                     entry['listName'] = policy_list_dict[entry['ref']]['name']
                        #                     entry['listType'] = policy_list_dict[entry['ref']]['type']
                        #                     entry.pop('ref')    
                        definition_list.append(definition_detail)
                return definition_list
            else:
                return []

    def get_policy_definition_dict(self, type, key_name='name', remove_key=False):

        policy_definition_list = self.get_policy_definition_list(type)

        return self.list_to_dict(policy_definition_list, key_name, remove_key=remove_key)

    def convert_definition_id_to_name(self, policy_definition):
        if 'assembly' in policy_definition:
            for assembly_item in policy_definition['assembly']:
                policy_definition_detail = self.get_policy_definition(assembly_item['type'].lower(), assembly_item['definitionId'])
                definition_id = assembly_item.pop('definitionId')
                if policy_definition_detail:
                    assembly_item['definitionName'] = policy_definition_detail['name']
                else:
                    raise Exception("Cannot find policy definition for {0}".format(definition_id))
                if 'entries' in assembly_item:
                    # Translate list IDs to names
                    self.convert_list_id_to_name(assembly_item['entries'])

    def convert_sequences_to_id(self, sequence_list):
        for sequence in sequence_list:
            if 'match' in sequence and 'entries' in sequence['match']:
                for entry in sequence['match']['entries']:
                    if 'listName' in entry:
                        policy_list_dict = self.get_policy_list_dict(entry['listType'])
                        if entry['listName'] in policy_list_dict:
                            entry['ref'] = policy_list_dict[entry['listName']]['listId']
                            entry.pop('listName')
                            entry.pop('listType')
                        else:
                            raise Exception("Could not find list {0} of type {1}".format(entry['listName'], entry['listType']))

    def get_central_policy_preview(self, policy_id):
        result = self.request('/template/policy/assembly/vsmart/{0}'.format(policy_id))

        try:
            return result['json']['preview']
        except:
            return None

    def export_policy_to_file(self, export_file):
        policy_lists_list = self.get_policy_list_list()
        policy_definitions_list = self.get_policy_definition_list()
        central_policies_list = self.get_central_policy_list()
        local_policies_list = self.get_local_policy_list()
        
        policy_export = {
            'vmanage_policy_lists': policy_lists_list,
            'vmanage_policy_definitions': policy_definitions_list,
            'vmanage_central_policies': central_policies_list,
            'vmanage_local_policies': local_policies_list
        }

        if export_file.endswith('.json'):
            with open(export_file, 'w') as outfile:
                json.dump(policy_export, outfile, indent=4, sort_keys=False)
        elif export_file.endswith('.yaml') or export_file.endswith('.yml'):
            with open(export_file, 'w') as outfile:
                yaml.dump(policy_export, outfile, default_flow_style=False)
        else:
            raise Exception("File format not supported")    

    def import_policy_from_file(self, file, update=False, check_mode=False, push=False):
        changed = False
        policy_list_updates = []
        policy_definition_updates = []
        central_policy_updates = []
        local_policy_updates = []

        # Read in the datafile
        if not os.path.exists(file):
            raise Exception('Cannot find file {0}'.format(file))
        with open(file) as f:
            if file.endswith('.yaml') or file.endswith('.yml'):
                policy_data = yaml.safe_load(f)
            else:
                policy_data = json.load(f)

        # Separate the feature template data from the device template data
        if 'vmanage_policy_lists' in policy_data:
            policy_list_data = policy_data['vmanage_policy_lists']
        else:
            policy_list_data = []
        if 'vmanage_policy_definitions' in policy_data:
            policy_definition_data = policy_data['vmanage_policy_definitions']
        else:
            policy_definition_data = []
        if 'vmanage_central_policies' in policy_data:
            central_policy_data = policy_data['vmanage_central_policies']
        else:
            central_policy_data = []
        if 'vmanage_local_policies' in policy_data:
            local_policy_data = policy_data['vmanage_local_policies']
        else:
            local_policy_data = []

        for policy_list in policy_list_data:
            # print("Importing Policy Lists")
            diff = self.import_policy_list(policy_list, check_mode=check_mode, update=update, push=push)
            if len(diff):
                policy_list_updates.append({'name': policy_list['name'], 'diff': diff})

        self.clear_policy_list_cache()

        for definition in policy_definition_data:
            # print("Importing Policy Definitions")
            diff = self.import_policy_definition(definition, check_mode=check_mode, update=update, push=push)
            if len(diff):
                policy_definition_updates.append({'name': definition['name'], 'diff': diff})

        for central_policy in central_policy_data:
            # print("Importing Central Policy")
            diff = self.import_central_policy(central_policy, check_mode=check_mode, update=update, push=push)
            if len(diff):
                central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})

        for local_policy in local_policy_data:
            # print("Importing Local Policy")
            diff = self.import_local_policy(local_policy, check_mode=check_mode, update=update, push=push)
            if len(diff):
                local_policy_updates.append({'name': local_policy['policyName'], 'diff': diff})

        return {
            'policy_list_updates': policy_list_updates,
            'policy_definition_updates': policy_definition_updates,
            'central_policy_updates': central_policy_updates,
            'local_policy_updates': local_policy_updates
        }

    def import_policy_list(self, policy_list, push=False, update=False, check_mode=False, force=False):
        diff = []
        # Policy Lists
        policy_list_dict = self.get_policy_list_dict(policy_list['type'], remove_key=False, cache=False)
        if policy_list['name'] in policy_list_dict:
            existing_list = policy_list_dict[policy_list['name']]
            diff = list(dictdiffer.diff(existing_list['entries'], policy_list['entries']))
            if diff:
                policy_list['listId'] = policy_list_dict[policy_list['name']]['listId']
                # If description is not specified, try to get it from the existing information
                if not policy_list['description']:
                    policy_list['description'] = policy_list_dict[policy_list['name']]['description']
                if not check_mode and update:
                    result = self.request('/template/policy/list/{0}/{1}'.format(policy_list['type'].lower(), policy_list['listId']),
                                    method='PUT', payload=policy_list)
                    if result['json']:
                        # Updating the policy list returns a `processId` that locks the list and 'masterTemplatesAffected'
                        # that lists the templates affected by the change.
                        if 'error' in result['json']:
                            raise Exception(result['json']['error']['message'])
                        elif 'processId' in result['json']:
                            process_id = result['json']['processId']
                            self.result['put_payload'] = response.json['processId']
                            if push:
                                # If told to push out the change, we need to reattach each template affected by the change
                                for template_id in result['json']['masterTemplatesAffected']:
                                    action_id = self.reattach_device_template(template_id)

                            # Delete the lock on the policy list
                            # FIXME: The list does not seem to update when we unlock too soon, so I think that we need
                            # to wait for the attachment, but need to understand this better.
                            response = self.request('/template/lock/{0}'.format(process_id), method='DELETE')
                        else:
                            raise Exception("Did not get a process id when updating policy list")
        else:
            diff = list(dictdiffer.diff({}, policy_list))
            if not check_mode:
                self.request('/template/policy/list/{0}/'.format(policy_list['type'].lower()),
                                method='POST', payload=policy_list)

        return diff

    def import_policy_definition(self, definition, update=False, push=False, check_mode=False, force=False):
        policy_definition_dict = self.get_policy_definition_dict(definition['type'], remove_key=False)
        diff = []
        payload = { 
            "name": definition['name'],
            "description": definition['description'],
            "type": definition['type'],
        }
        if 'defaultAction' in definition:
            payload.update({'defaultAction': definition['defaultAction']})           
        if 'sequences' in definition:
            payload.update({'sequences': definition['sequences']})        
        if 'definition' in definition:
            payload.update({'definition': definition['definition']})

        if definition['name'] in policy_definition_dict:
            existing_definition = policy_definition_dict[definition['name']]
            if 'defaultAction' in payload:
                diff.extend(list(dictdiffer.diff(existing_definition['defaultAction'], payload['defaultAction'])))           
            if 'sequences' in payload:
                diff.extend(list(dictdiffer.diff(existing_definition['sequences'], payload['sequences'])))        
            if 'definition' in payload:
                diff.extend(list(dictdiffer.diff(existing_definition['definition'], payload['definition'])))            
            if len(diff):
                if 'definition' in definition:
                    self.convert_list_name_to_id(definition['definition'])
                if 'sequences' in definition:
                    self.convert_sequences_to_id(definition['sequences'])
                if 'rules' in definition:
                    self.convert_sequences_to_id(definition['rules'])                      
                if not check_mode and update:
                    self.request('/template/policy/definition/{0}/{1}'.format(definition['type'].lower(), policy_definition_dict[definition['name']]['definitionId']),
                                    method='PUT', payload=payload)
        else:
            diff = list(dictdiffer.diff({}, payload))
            # List does not exist
            if 'definition' in definition:
                self.convert_list_name_to_id(definition['definition'])
            if 'sequences' in definition:
                self.convert_list_name_to_id(definition['sequences']) 
            if 'rules' in definition:
                self.convert_list_name_to_id(definition['rules'])        
            if not check_mode:
                self.request('/template/policy/definition/{0}/'.format(definition['type'].lower()),
                                method='POST', payload=payload)

        return diff

    def convert_definition_name_to_id(self, policy_definition):
        if 'assembly' in policy_definition:
            for assembly_item in policy_definition['assembly']:
                definition_name = assembly_item.pop('definitionName')
                policy_definition_dict = self.get_policy_definition_dict(assembly_item['type'])
                if definition_name in policy_definition_dict:
                    assembly_item['definitionId'] = policy_definition_dict[definition_name]['definitionId']
                else:
                    raise Exception("Cannot find policy definition {0}".format(definition_name))
                if 'entries' in assembly_item:
                    self.convert_list_name_to_id(assembly_item['entries'])

#
# Central Policy
#
    def get_central_policy_list(self):
        result = self.request('/template/policy/vsmart')
        if 'data' in result['json']:
            central_policy_list = result['json']['data']
            for policy in central_policy_list:
                try:
                    json_policy = json.loads(policy['policyDefinition'])
                    policy['policyDefinition'] = json_policy
                except:
                    pass
                # policy['policyDefinition'] = json.loads(policy['policyDefinition'])
                self.convert_definition_id_to_name(policy['policyDefinition'])
            return central_policy_list
        else:
            return []

    def get_central_policy_dict(self, key_name='policyName', remove_key=False):

        central_policy_list = self.get_central_policy_list()

        return self.list_to_dict(central_policy_list, key_name, remove_key=remove_key)

    def import_central_policy(self, central_policy, update=False, push=False, check_mode=False, force=False):
        diff = []
        central_policy_dict = self.get_central_policy_dict(remove_key=True)
        payload = {
            'policyName': central_policy['policyName']
        }
        payload['policyDescription'] = central_policy['policyDescription']
        payload['policyType'] = central_policy['policyType']
        payload['policyDefinition'] = central_policy['policyDefinition']
        if payload['policyName'] in central_policy_dict:
            # A policy by that name already exists
            existing_policy = central_policy_dict[payload['policyName']]
            diff = list(dictdiffer.diff(existing_policy['policyDefinition'], payload['policyDefinition']))
            if len(diff):
                # Convert list and definition names to template IDs
                if 'policyDefinition' in payload:
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode and update:
                    self.request('/template/policy/vsmart/{0}'.format(existing_policy['policyId']), method='PUT', payload=payload)
        else:
            diff = list(dictdiffer.diff({}, payload['policyDefinition']))
            if not check_mode:
                # Convert list and definition names to template IDs
                if 'policyDefinition' in payload:
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                self.request('/template/policy/vsmart', method='POST', payload=payload)        
        return diff

#
# Local Policy
#
    def get_local_policy_list(self):
        result = self.request('/template/policy/vedge')
        if 'data' in result['json']:
            local_policy_list = result['json']['data']
            for policy in local_policy_list:
                # This is to accommodate CLI policy
                try:
                    json_policy = json.loads(policy['policyDefinition'])
                    policy['policyDefinition'] = json_policy
                except:
                    pass
                # policy['policyDefinition'] = json.loads(policy['policyDefinition'])
                self.convert_definition_id_to_name(policy['policyDefinition'])
            return local_policy_list
        else:
            return []

    def get_local_policy_dict(self, key_name='policyName', remove_key=False):

        local_policy_list = self.get_local_policy_list()

        return self.list_to_dict(local_policy_list, key_name, remove_key=remove_key)

    def import_local_policy(self, local_policy, update=False, push=False, check_mode=False, force=False):
        diff = []
        changes = False
        local_policy_dict = self.get_local_policy_dict(remove_key=False)
        payload = {
            'policyName': local_policy['policyName']
        }
        payload['policyDescription'] = local_policy['policyDescription']
        payload['policyType'] = local_policy['policyType']
        payload['policyDefinition'] = local_policy['policyDefinition']
        if payload['policyName'] in local_policy_dict:
            # A policy by that name already exists
            existing_policy = local_policy_dict[payload['policyName']]
            diff = list(dictdiffer.diff(existing_policy['policyDefinition'], payload['policyDefinition']))
            if len(diff):
                if 'policyDefinition' in payload:
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode and update:
                    self.request('/template/policy/vedge/{0}'.format(existing_policy['policyId']), method='PUT', payload=payload)
        else:
            diff = list(dictdiffer.diff({}, payload['policyDefinition']))
            if 'policyDefinition' in payload:
                # Convert list and definition names to template IDs
                self.convert_definition_name_to_id(payload['policyDefinition'])
            if not check_mode:
                self.request('/template/policy/vedge', method='POST', payload=payload)        
        return diff

#
# Show commands
#
    def get_control_connections(self, device_ip):
        result = self.request('/device/control/connections?deviceId={0}'.format(device_ip))

        try:
            return result['json']['data']
        except:
            return {}

    def get_control_connections_history(self, device_ip):
        result = self.request('/device/control/connectionshistory?deviceId={0}'.format(device_ip))

        try:
            return result['json']['data']
        except:
            return {}

    def get_device_data(self, path, device_ip):
        result = self.request('/device/{0}?deviceId={1}'.format(path, device_ip))

        try:
            return result['json']['data']
        except:
            return {}

    def reattach_device_template(self, template_id):
        device_list = self.get_template_attachments(template_id, key='uuid')
        # First, we need to get the input to feed to the re-attach
        payload = {
            "templateId": template_id,
            "deviceIds": device_list,
            "isEdited": "true",
            "isMasterEdited": "false"
        }
        result = self.request('/template/device/config/input/', method='POST', payload=payload)
        # Then we feed that to the attach
        if result['json'] and 'data' in result['json']:
            payload = {
                "deviceTemplateList":
                    [
                        {
                            "templateId": template_id,
                            "device": response.json['data'],
                            "isEdited": "true",
                            "isMasterEdited": "false"
                        }
                    ]
            }
            result = self.request('/template/device/config/attachfeature', method='POST', payload=payload)
            if result['json'] and 'id' in result['json']:
                # Need to check 'action_status' here
                self.waitfor_action_completion(result['json']['id'])
            else:
                raise Exception(msg='Did not get action ID after attaching device to template.')
        else:
            raise Exception(msg="Could not retrieve input for template {0}".format(template_id))
        return result['json']['id']

    def waitfor_action_completion(self, action_id):
        status = 'in_progress'
        response = {}
        while status == "in_progress":
            result = self.request('/device/action/status/{0}'.format(action_id))
            if result['json']:
                status = result['json']['summary']['status']
                if 'data' in result['json'] and result['json']['data']:
                    action_status = result['json']['data'][0]['statusId']
                    action_activity = result['json']['data'][0]['activity']
                    if 'actionConfig' in result['json']['data'][0]:
                        action_config = result['json']['data'][0]['actionConfig']
                    else:
                        action_config = None
            else:
                raise Exception(msg="Unable to get action status: No response")
            time.sleep(10)

        # if self.result['action_status'] == 'failure':
        #    self.fail_json(msg="Action failed")
        return {
            'action_response': result['json'],
            'action_id': action_id,
            'action_status': action_status,
            'action_activity': action_activity,
            'action_config': action_config
        }