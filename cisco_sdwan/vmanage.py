from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import requests
import re
import time
import os
from collections import OrderedDict
import urllib3
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
        else:
            return response

    def request(self, url_path, method='GET', headers=STANDARD_JSON_HEADER, data=None, files=None, payload=None, status_codes=VALID_STATUS_CODES):
        """Generic HTTP method for viptela requests."""
        url = '{0}{1}'.format(self.base_url, url_path)
        if payload:
            data = json.dumps(payload, sort_keys=False)

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
        dict = OrderedDict()
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

    def get_device_config_list(self, type):
        result = self.request('/system/device/{0}'.format(type))

        try:
            return result['json']['data']
        except:
            return []

    def get_device_config_dict(self, type, key_name='host-name', remove_key=False):

        device_list = self.get_device_config_list(type)

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

#
# Templates
#

    def get_device_template_list(self, factory_default=False):
        result = self.request('/template/device')

        return_list = []
        if 'data' in result['json']:
            device_body = result['json']
            feature_template_dict = self.get_feature_template_dict(factory_default=True, key_name='templateId')
            for device in device_body['data']:
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

                    return_list.append(object)

        return return_list

    def get_device_template_dict(self, factory_default=False, key_name='templateName', remove_key=True):
        device_template_list = self.get_device_template_list(factory_default=factory_default)

        return self.list_to_dict(device_template_list, key_name, remove_key)

    def get_feature_template_list(self, factory_default=False):
        result = self.request('/template/feature')

        return_list = []
        if 'json' in result:
            template_list = result['json']['data']
            for template in template_list:
                if not factory_default and template['factoryDefault']:
                    continue
                template['templateDefinition'] = json.loads(template['templateDefinition'], object_pairs_hook=OrderedDict)
                template.pop('editedTemplateDefinition', None)
                return_list.append(template)

        return return_list

    def get_feature_template_dict(self, factory_default=False, key_name='templateName', remove_key=True):
        feature_template_list = self.get_feature_template_list(factory_default=factory_default)

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
    def export_templates_to_file(self, file):
        feature_template_list = self.get_feature_template_list()
        device_template_list = self.get_device_template_list()
        template_export = OrderedDict()

        template_export = {
            'feature_templates': feature_template_list,
            'device_templates': device_template_list
        }

        with open(file, 'w') as f:
            json.dump(template_export, f, indent=4, sort_keys=False)

    def import_templates_from_file(self, file, update=False, check_mode=False, force=False):
        changed = False
        feature_template_updates = 0
        device_template_updates = 0
        template_data = OrderedDict()
        feature_template_data = OrderedDict()

        # Read in the datafile
        if not os.path.exists(file):
            raise Exception(msg='Cannot find file {0}'.format(file))
        with open(file) as f:
            template_data = json.load(f, sort_keys=False)

        # Separate the feature template data from the device template data
        feature_template_data = template_data['feature_templates']
        device_template_data = template_data['device_templates']

        # Process the feature templates
        feature_template_dict = self.get_feature_template_dict(factory_default=True)
        for feature_template in feature_template_data:
            if feature_template['templateName'] in feature_template_dict:
                # Need to figure out how to update feature templates
                if update:
                    feature_template_updates = feature_template_updates + 1
                    if not check_mode:
                        self.add_feature_template(feature_template)
            else:
                feature_template_updates = feature_template_updates + 1
                if not check_mode:
                    self.add_feature_template(feature_template)                

        # Process the device templates
        device_template_dict = self.get_device_template_dict()
        for device_template in device_template_data:
            if device_template['templateName'] in device_template_dict:
                # Need to figure out how to update device templates
                if update:
                    device_template_updates = device_template_updates + 1
                    if not check_mode:
                        self.add_device_template(device_template)
            else:
                device_template_updates = device_template_updates + 1
                if not check_mode:
                    self.add_device_template(device_template)

        return {'changed': True if device_template_updates + feature_template_updates > 0 else False,
                'feature_template_updates': feature_template_updates,
                'device_template_updates': device_template_updates,
                }        

    def add_feature_template(self, feature_template):
        payload = OrderedDict()
        payload = {
            'templateName': feature_template['templateName'],
            'templateDescription': feature_template['templateDescription'],
            'deviceType': feature_template['deviceType'],
            'templateDefinition': feature_template['templateDefinition'],
            'templateType': feature_template['templateType'],
            'templateMinVersion': feature_template['templateMinVersion'],
            'factoryDefault': feature_template['factoryDefault'],
            'configType': feature_template['configType'],
            'feature': feature_template['feature'],
        }
        return self.request('/template/feature/', method='POST', data=json.dumps(payload, sort_keys=False))

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
    def get_policy_list(self, type, list_id):
        result = self.request('/template/policy/list/{0}/{1}'.format(type.lower(), list_id))
        return result['json']

    def get_policy_list_list(self, type='all'):
        if type == 'all':
            result = self.request('/template/policy/list', status_codes=[200])
        else:
            result = self.request('/template/policy/list/{0}'.format(type.lower()), status_codes=[200, 404])

        if result['status_code'] == 404:
            return []
        else:
            return result['json']['data']

    def get_policy_list_dict(self, type='all', key_name='name', remove_key=False):

        policy_list = self.get_policy_list_list(type)

        return self.list_to_dict(policy_list, key_name, remove_key=remove_key)

    def get_policy_definition(self, type, definition_id):
        result = self.request('/template/policy/definition/{0}/{1}'.format(type, definition_id))
        return result['json']

    def get_policy_definition_list(self, type='all'):
        if type == 'all':
            policy_definitions = {}
            policy_list_dict = self.get_policy_list_dict('all', key_name='listId')
            # Get a list of hub-and-spoke becuase it tells us the other definition types
            # known by this server (hopefully)
            definition_types = []
            result = self.request('/template/policy/definition/hubandspoke')
            try:
                definition_type_titles = result['json']['header']['columns'][1]['keyvalue']
            except:
                raise Exception('Could not retrieve definition types')
            for definition_type in definition_type_titles:
                definition_types.append(definition_type['key'].lower())

            for list_type in definition_types:
                definition_list = self.get_policy_definition_list(list_type)
                for definition in definition_list:
                    definition_detail = self.get_policy_definition(list_type, definition['definitionId'])
                    if 'sequences' in definition_detail:
                        # We need to translate policy lists IDs to name
                        for sequence in definition_detail['sequences']:
                                if 'match' in sequence and 'entries' in sequence['match']:
                                    pass
                                    for entry in sequence['match']['entries']:
                                        if 'ref' in entry:
                                            entry['listName'] = policy_list_dict[entry['ref']]['name']
                                            entry['listType'] = policy_list_dict[entry['ref']]['type']
                if definition_detail:
                    policy_definitions[list_type] = definition_detail
            return policy_definitions
        else:
            result = self.request('/template/policy/definition/{0}'.format(type))
            try:
                return result['json']['data']
            except:
                return {}

    def get_policy_definition_dict(self, type, key_name='name', remove_key=False):

        policy_definition_list = self.get_policy_definition_list(type)

        return self.list_to_dict(policy_definition_list, key_name, remove_key=remove_key)

    def get_central_policy_list(self):
        result = self.request('/template/policy/vsmart')
        if 'data' in result['json']:
            central_policy_list = result['json']['data']
            for policy in central_policy_list:
                policy['policyDefinition'] = json.loads(policy['policyDefinition'])
                for item in policy['policyDefinition']['assembly']:
                    policy_definition = self.get_policy_definition(item['type'].lower(), item['definitionId'])
                    item['definitionName'] = policy_definition['name']
                    #
                    # Translate list IDs to names
                    #
                    if 'entries' in item:
                        for entry in item['entries']:
                            for key, list in entry.items():
                                if key in POLICY_LIST_DICT:
                                    for index, list_id in enumerate(list):
                                        policy_list = self.get_policy_list(POLICY_LIST_DICT[key], list_id)
                                        list[index] = policy_list['name']
            return central_policy_list
        else:
            return []

    def get_central_policy_dict(self, type, key_name='policyName', remove_key=False):

        central_policy_list = self.get_policy_definition_list(type)

        return self.list_to_dict(central_policy_list, key_name, remove_key=remove_key)

    def get_central_policy_preview(self, policy_id):
        result = self.request('/template/policy/assembly/vsmart/{0}'.format(policy_id))

        try:
            return result['json']['preview']
        except:
            return None

    def get_local_policy_list(self):
        result = self.request('/template/policy/vedge')
        if 'data' in result['json']:
            local_policy_list = result['json']['data']
            for policy in local_policy_list:
                policy['policyDefinition'] = json.loads(policy['policyDefinition'])
                for item in policy['policyDefinition']['assembly']:
                    policy_definition = self.get_policy_definition(item['type'].lower(), item['definitionId'])
                    item['definitionName'] = policy_definition['name']
                #     #
                #     # Translate list IDs to names
                #     #
                #     if 'entries' in item:
                #         for entry in item['entries']:
                #             for key, list in entry.items():
                #                 if key in POLICY_LIST_DICT:
                #                     for index, list_id in enumerate(list):
                #                         policy_list = self.get_policy_list(POLICY_LIST_DICT[key], list_id)
                #                         list[index] = policy_list['name']
            return local_policy_list
        else:
            return []

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

    def export_policy_to_file(self, file):
        policy_lists_list = self.get_policy_list_list()
        policy_definitions_list = self.get_policy_definition_list()
        central_policies_list = self.get_central_policy_list()
        local_policies_list = self.get_central_policy_list()
        
        policy_export = {
            'policy_lists': policy_lists_list,
            'policy_definitions': policy_definitions_list,
            'central_policies': central_policies_list,
            'local_policies': local_policies_list
        }

        with open(file, 'w') as f:
            json.dump(policy_export, f, indent=4, sort_keys=False)

    def import_policy_from_file(self, file, update=False, check_mode=False, force=False):
        changed = False
        policy_list_updates = 0
        policy_definition_updates = 0
        central_policy_updates = 0

        # Read in the datafile
        if not os.path.exists(file):
            raise Exception(msg='Cannot find file {0}'.format(file))
        with open(file) as f:
            policy_data = json.load(f)

        # Separate the feature template data from the device template data
        policy_list_data = policy_data['policy_lists']
        policy_definition_data = policy_data['policy_definitions']
        central_policy_data = policy_data['central_policies']

        for policy_list in policy_list_data:
            if self.import_policy_list(policy_list, update=update, force=force):
                policy_list_updates = policy_list_updates + 1

        for type, definition_list in policy_definition_data.items():
            for definition in definition_list:
                if self.import_policy_definition(definition, update=update, force=force):
                    policy_definition_updates = policy_definition_updates + 1

        for central_policy in central_policy_data:
            if self.import_central_policy(central_policy, update=update, force=force):
                central_policy_updates = central_policy_updates + 1

        return {
            'policy_list_updates': policy_list_updates,
            'policy_definition_updates': policy_definition_updates,
            'central_policy_updates': central_policy_updates
        }

    def import_policy_list(self, list, push=False, update=False, check_mode=False, force=False):
        changed = False
        # Policy Lists
        policy_list_dict = self.get_policy_list_dict('all', remove_key=False)
        if list['name'] in policy_list_dict:
            if update:
                # FIXME Just compare the entries for now.
                if list['entries'] != policy_list_dict[list['name']]['entries'] or force:
                    changed = True
                    list['listId'] = policy_list_dict[list['name']]['listId']
                    # If description is not specified, try to get it from the existing information
                    if not list['description']:
                        list['description'] = policy_list_dict[list['name']]['description']
                    if not check_mode:
                        result = self.request('/template/policy/list/{0}/{1}'.format(list['type'].lower(), list['listId']),
                                        method='PUT', payload=list)
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
            if not check_mode:
                self.request('/template/policy/list/{0}/'.format(list['type'].lower()),
                                method='POST', payload=list)
            changed = True

        return changed

    def import_policy_definition(self, list, update=False, push=False, check_mode=False, force=False):
        policy_definition_dict = self.get_policy_definition_dict(list['type'], remove_key=False)
        changed = False
        payload = {
            "name": list['name'],
            "description": list['description'],
            "type": list['type'],
            "sequences": list['sequences'],
            "defaultAction": list['defaultAction']
        }
        if list['name'] in policy_definition_dict:
            # List already exist
            if update:
                changed_items = self.compare_payloads(list, policy_definition_dict[list['name']], compare_values=compare_values)
                if changed_items:
                    changed = True
                    payload['sequences'] = self.convert_sequences_to_id(list['sequences'])
                    if not check_mode:
                        self.request('/template/policy/definition/{0}/{1}'.format(list['type'], policy_definition_dict[list['name']]['definitionId']),
                                        method='PUT', payload=payload)
        else:
            # List does not exist
            payload['sequences'] = self.convert_sequences_to_id(list['sequences'])
            if not check_mode:
                self.request('/template/policy/definition/{0}/'.format(list['type']),
                                method='POST', payload=payload)
            changed = True

        return changed

    def convert_sequences_to_id(self, sequence_list):
        for sequence in sequence_list:
            for entry in sequence['match']['entries']:
                policy_list_dict = self.get_policy_list_dict(entry['listType'])
                if entry['listName'] in policy_list_dict:
                    entry['ref'] = policy_list_dict[entry['listName']]['listId']
                    entry.pop('listName')
                    entry.pop('listType')
                else:
                    raise Exception("Could not find list {0} of type {1}".format(entry['listName'], entry['listType']))
        return sequence_list

    def import_central_policy(self, central_policy, update=False, push=False, check_mode=False, force=False):
        changed = False
        central_policy_dict = self.get_central_policy_dict(remove_key=False)
        payload = {
            'policyName': central_policy['policyName']
        }
        payload['policyDescription'] = central_policy['policyDescription']
        payload['policyType'] = central_policy['policyType']
        payload['policyDefinition'] = central_policy['policyDefinition']
        # If a template by that name is already there
        if payload['policyName'] in central_policy_dict:
            changed = False
            # changed_items = viptela.compare_payloads(payload, device_template_dict[payload['templateName']], compare_values=compare_values)
            # if changed_items:
            #     viptela.result['changed'] = True
            #     viptela.result['what_changed'] = changed_items
            #     viptela.result['old_payload'] = device_template_dict[payload['templateName']]
            #     if not module.check_mode:
            #         #
            #         # Convert template names to template IDs
            #         #
            #         if payload['configType'] == 'template':
            #             payload['generalTemplates'] = viptela.generalTemplates_to_id(device_template['generalTemplates'])
            #         viptela.request('/dataservice/template/device/feature/{0}'.format(device_template_dict[payload['templateName']]['templateId']),
            #                         method='PUT', payload=payload)
        else:
            if not check_mode:
                #
                # Convert list and definition names to template IDs
                #
                regex = re.compile(r'^(?P<type>.*)Lists$')
                for policy_item in central_policy['policyDefinition']['assembly']:
                    definition_name = policy_item.pop('definitionName')
                    policy_definition_dict = self.get_policy_definition_dict(policy_item['type'])
                    if definition_name in policy_definition_dict:
                        policy_item['definitionId'] = policy_definition_dict[definition_name]['definitionId']
                    else:
                        raise Exception("Cannot find policy definition {0}".format(definition_name))
                    for entry in policy_item['entries']:
                        for list_type, list in entry.items():
                            match = regex.search(list_type)
                            if match:
                                type = match.groups('type')[0]
                                if type in POLICY_LIST_TYPES:
                                    policy_list_dict = self.get_policy_list_dict(type)
                                    for index, list_name in enumerate(list):
                                        list[index] = policy_list_dict[list_name]['listId']
                                else:
                                    raise Exception("Cannot find list type {0}".format(type))

                self.request('/template/policy/vsmart', method='POST', payload=payload)
                changed = True
        
        return changed

    def get_central_policy_dict(self, key_name='policyName', remove_key=False):

        central_policy_list = self.get_central_policy_list()

        return self.list_to_dict(central_policy_list, key_name, remove_key=remove_key)