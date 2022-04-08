import json
import requests
import re
import sys
import time
from ansible.module_utils.basic import AnsibleModule, json, env_fallback
from collections import OrderedDict

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

def viptela_argument_spec():
    return dict(host=dict(type='str', required=True, fallback=(env_fallback, ['VMANAGE_HOST'])),
                port=dict(type='str', required=False, fallback=(env_fallback, ['VMANAGE_PORT'])),
                user=dict(type='str', required=True, fallback=(env_fallback, ['VMANAGE_USERNAME'])),
                password=dict(type='str', required=True, fallback=(env_fallback, ['VMANAGE_PASSWORD'])),
                validate_certs=dict(type='bool', required=False, default=False),
                timeout=dict(type='int', default=30)
                )


STANDARD_HTTP_TIMEOUT = 10
STANDARD_JSON_HEADER = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}
POLICY_LIST_DICT = {
    'siteLists': 'site',
    'vpnLists': 'vpn',
}
VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]


class viptelaModule(object):

    def __init__(self, module, function=None):
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.headers = dict()
        self.function = function
        self.cookies = None
        self.json = None

        self.method = None
        self.path = None
        self.response = None
        self.status = None
        self.url = None
        self.params['force_basic_auth'] = True
        self.user = self.params['user']
        self.password = self.params['password']
        self.host = self.params['host']
        self.timeout = self.params['timeout']
        self.modifiable_methods = ['POST', 'PUT', 'DELETE']

        self.session = requests.Session()
        self.session.verify = self.params['validate_certs']

        self.POLICY_DEFINITION_TYPES = ['cflowd', 'dnssecurity', 'control', 'hubandspoke', 'acl', 'vpnmembershipgroup',
                                        'mesh', 'rewriterule', 'data', 'rewriterule', 'aclv6']
        self.POLICY_LIST_TYPES = ['community', 'localdomain', 'ipv6prefix', 'dataipv6prefix', 'tloc', 'aspath', 'zone',
                                  'color', 'sla', 'app', 'mirror', 'dataprefix', 'extcommunity', 'site', 'ipprefixall',
                                  'prefix', 'umbrelladata', 'class', 'ipssignature', 'dataprefixall',
                                  'urlblacklist', 'policer', 'urlwhitelist', 'vpn']

        self.login()

    # Deleting (Calling destructor)
    # def __del__(self):
    #     self.logout()

    def _fallback(self, value, fallback):
        if value is None:
            return fallback
        return value

    def list_to_dict(self, list, key_name, remove_key=True):
        dict_value = OrderedDict()
        for item in list:
            if key_name in item:
                if remove_key:
                    key = item.pop(key_name)
                else:
                    key = item[key_name]

                dict_value[key] = item
            # else:
            #     self.fail_json(msg="key {0} not found in dictionary".format(key_name))

        return dict_value

    @staticmethod
    def compare_payloads(new_payload, old_payload, compare_values=None):
        if compare_values is None:
            compare_values = []
        payload_key_diff = []
        for key, value in new_payload.items():
            if key in compare_values:
                if key not in old_payload or new_payload[key] != old_payload[key]:
                    payload_key_diff.append(key)
        return payload_key_diff

    def login(self):
        # self.session.headers.update({'Connection': 'keep-alive', 'Content-Type': 'application/json'})

        try:
            response = self.session.post(
                url='https://{0}/j_security_check'.format(self.host),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'j_username': self.user, 'j_password': self.password},
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            self.module.fail_json(msg=e)

        if response.text.startswith('<html>'):
            self.fail_json(msg='Could not login to device, check user credentials.', **self.result)

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
            self.fail_json(msg='Failed getting X-XSRF-TOKEN: {0}'.format(response.status_code))

        return response

    def logout(self):
        self.request('/dataservice/settings/clientSessionTimeout')
        self.request('/logout')

    def request(self, url_path, method='GET', data=None, files=None, payload=None, status_codes=None):
        """Generic HTTP method for viptela requests."""

        if status_codes is None:
            status_codes = VALID_STATUS_CODES
        self.method = method
        self.url = 'https://{0}{1}'.format(self.host, url_path)
        self.result['url'] = self.url
        self.result['headers'] = self.session.headers.__dict__
        if files is None:
            self.session.headers['Content-Type'] = 'application/json'

        if payload:
            self.result['payload'] = payload
            data = json.dumps(payload)
            self.result['data'] = data

        response = self.session.request(method, self.url, files=files, data=data)

        self.status_code = response.status_code
        self.status = requests.status_codes._codes[response.status_code][0]
        decoded_response = {}
        if self.status_code not in status_codes:
            try:
                decoded_response = response.json()
            except JSONDecodeError:
                pass

            if 'error' in decoded_response:
                error = 'Unknown'
                details = 'Unknown'
                if 'details' in decoded_response['error']:
                    details = decoded_response['error']['details']
                if 'message' in decoded_response['error']:
                    error = decoded_response['error']['message']
                self.fail_json(msg='{0}: {1}'.format(error, details))
            else:
                self.fail_json(msg=self.status)

        try:
            response.json = response.json()
        except JSONDecodeError:
            response.json = {}

        return response

    def get_template_attachments(self, template_id, key='host-name'):
        response = self.request('/dataservice/template/device/config/attached/{0}'.format(template_id))

        attached_devices = []
        if response.json:
            device_list = response.json['data']
            for device in device_list:
                attached_devices.append(device[key])

        return attached_devices

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

    def convert_sequences_to_id(self, sequence_list):
        for sequence in sequence_list:
            for entry in sequence['match']['entries']:
                policy_list_dict = self.get_policy_list_dict(entry['listType'])
                if entry['listName'] in policy_list_dict:
                    entry['ref'] = policy_list_dict[entry['listName']]['listId']
                    entry.pop('listName')
                    entry.pop('listType')
                else:
                    self.fail_json(msg="Could not find list {0} of type {1}".format(entry['listName'], entry['listType']))
        return sequence_list

    def get_device_status(self, value, key='system-ip'):
        response = self.request('/dataservice/device?{0}={1}'.format(key, value))

        try:
            return response.json['data'][0]
        except:
            return {}

    def get_device_template_list(self, factory_default=False):
        response = self.request('/dataservice/template/device')

        return_list = []
        if response.json:

            device_body = response.json
            feature_template_dict = self.get_feature_template_dict(factory_default=True, key_name='templateId')

            for device in device_body['data']:
                object_response = self.request('/dataservice/template/device/object/{0}'.format(device['templateId']))
                if object_response.json:
                    object_value = object_response.json
                    if not factory_default and object_value['factoryDefault']:
                        continue

                    if 'generalTemplates' in object_value:
                        generalTemplates = []
                        for old_template in object_value.pop('generalTemplates'):
                            new_template = {
                                'templateName': feature_template_dict[old_template['templateId']]['templateName'],
                                'templateType': old_template['templateType']}
                            if 'subTemplates' in old_template:
                                subTemplates = []
                                for sub_template in old_template['subTemplates']:
                                    subTemplates.append({'templateName': feature_template_dict[sub_template['templateId']]['templateName'],
                                                         'templateType': sub_template['templateType']})
                                new_template['subTemplates'] = subTemplates

                            generalTemplates.append(new_template)
                        object_value['generalTemplates'] = generalTemplates

                    object_value['templateId'] = device['templateId']
                    object_value['attached_devices'] = self.get_template_attachments(device['templateId'])
                    object_value['input'] = self.get_template_input(device['templateId'])

                    return_list.append(object_value)

        return return_list

    def get_device_template_dict(self, factory_default=False, key_name='templateName', remove_key=True):
        device_template_list = self.get_device_template_list(factory_default=factory_default)

        return self.list_to_dict(device_template_list, key_name, remove_key)

    def get_feature_template_list(self, factory_default=False):
        response = self.request('/dataservice/template/feature')

        return_list = []
        if response.json:
            template_list = response.json['data']
            for template in template_list:
                if not factory_default and template['factoryDefault']:
                    continue
                template['templateDefinition'] = json.loads(template['templateDefinition'])
                template.pop('editedTemplateDefinition', None)
                return_list.append(template)

        return return_list

    def get_feature_template_dict(self, factory_default=False, key_name='templateName', remove_key=True):
        feature_template_list = self.get_feature_template_list(factory_default=factory_default)

        return self.list_to_dict(feature_template_list, key_name, remove_key)

    def get_policy_list(self, type, list_id):
        response = self.request('/dataservice/template/policy/list/{0}/{1}'.format(type.lower(), list_id))
        return response.json

    def get_policy_list_list(self, type='all'):
        if type == 'all':
            response = self.request('/dataservice/template/policy/list', status_codes=[200, 404])
        else:
            response = self.request('/dataservice/template/policy/list/{0}'.format(type.lower()), status_codes=[200, 404])

        if response.status_code == 404:
            return []
        else:
            return response.json['data']

    def get_policy_list_dict(self, type, key_name='name', remove_key=False):

        policy_list = self.get_policy_list_list(type)

        return self.list_to_dict(policy_list, key_name, remove_key=remove_key)

    def get_policy_definition(self, type, definition_id):
        response = self.request('/dataservice/template/policy/definition/{0}/{1}'.format(type, definition_id))
        return response.json

    def get_policy_definition_list(self, type):
        response = self.request('/dataservice/template/policy/definition/{0}'.format(type))

        return response.json['data']

    def get_vmanage_org(self):
        response = self.request('/dataservice/settings/configuration/organization')
        try:
            return response.json['data'][0]['org']
        except:
            return None

    def set_vmanage_org(self, org):
        payload = {'org': org}
        response = self.request('/dataservice/settings/configuration/organization', method='POST', payload=payload)

        return response.json['data']

    def get_vmanage_vbond(self):
        response = self.request('/dataservice/settings/configuration/device')
        try:
            return {'vbond': response.json['data'][0]['domainIp'], 'vbond_port': response.json['data'][0]['port']}
        except:
            return {'vbond': None, 'vbond_port': None}

    def set_vmanage_vbond(self, vbond, vbond_port='12346'):
        payload = {'domainIp': vbond, 'port': vbond_port}
        self.request('/dataservice/settings/configuration/device', method='POST', payload=payload)
        return

    def get_vmanage_ca_type(self):
        response = self.request('/dataservice/settings/configuration/certificate')
        try:
            return response.json['data'][0]['certificateSigning']
        except:
            return None

    def set_vmanage_ca_type(self, type):
        payload = {'certificateSigning': type, 'challengeAvailable': 'false'}
        self.request('/dataservice/settings/configuration/certificate', method='POST', payload=payload)
        return

    def get_vmanage_root_cert(self):
        response = self.request('/dataservice/certificate/rootcertificate')
        try:
            return response.json['rootcertificate']
        except:
            return None

    def set_vmanage_root_cert(self, cert):
        payload = {'enterpriseRootCA': cert}
        self.request('/dataservice/settings/configuration/certificate/enterpriserootca', method='PUT', payload=payload)
        return

    def install_device_cert(self, cert):
        response = self.request('/dataservice/certificate/install/signedCert', method='POST', data=cert)
        if response.json and 'id' in response.json:
            self.waitfor_action_completion(response.json['id'])
        else:
            self.fail_json(msg='Did not get action ID after attaching device to template.')
        return response.json['id']

    def get_policy_definition_dict(self, type, key_name='name', remove_key=False):

        policy_definition_list = self.get_policy_definition_list(type)

        return self.list_to_dict(policy_definition_list, key_name, remove_key=remove_key)

    def get_central_policy_list(self):
        response = self.request('/dataservice/template/policy/vsmart')
        if response.json:
            central_policy_list = response.json['data']
            for policy in central_policy_list:
                policy['policyDefinition'] = json.loads(policy['policyDefinition'])
                for item in policy['policyDefinition']['assembly']:
                    policy_definition = self.get_policy_definition(item['type'], item['definitionId'])
                    item['definitionName'] = policy_definition['name']
                    for entry in item['entries']:
                        for key, list in entry.items():
                            if key in POLICY_LIST_DICT:
                                for index, list_id in enumerate(list):
                                    policy_list = self.get_policy_list(POLICY_LIST_DICT[key], list_id)
                                    list[index] = policy_list['name']
            #     if 'policyDefinition' in policy:
            #         for old_template in policy.pop('policyDefinition'):
            #

            return central_policy_list
        else:
            return []

    def get_central_policy_dict(self, key_name='policyName', remove_key=False):

        central_policy_list = self.get_central_policy_list()

        return self.list_to_dict(central_policy_list, key_name, remove_key=remove_key)

    def get_unused_device(self, model):
        response = self.request('/dataservice/system/device/vedges?model={0}&state=tokengenerated'.format(model))

        if response.json:
            try:
                return response.json['data'][0]
            except:
                return response.json['data']
        else:
            return {}

    def get_device_by_state(self, state, type='vedges'):
        response = self.request('/dataservice/system/device/{0}?state={1}'.format(type, state))

        if response.json:
            try:
                return response.json['data'][0]
            except:
                return response.json['data']
        else:
            return {}

    def get_device_by_uuid(self, uuid, type='vedges'):
        response = self.request('/dataservice/system/device/{0}?uuid={1}'.format(type, uuid))

        if response.json:
            try:
                return response.json['data'][0]
            except:
                return response.json['data']
        else:
            return {}

    def get_device_by_device_ip(self, device_ip, type='vedges'):
        response = self.request('/dataservice/system/device/{0}?deviceIP={1}'.format(type, device_ip))

        if response.json:
            try:
                return response.json['data'][0]
            except:
                return response.json['data']
        else:
            return {}

    def get_device_by_name(self, name, type='vedges'):
        device_dict = self.get_device_dict(type)

        try:
            return device_dict[name]
        except:
            return {}

    def get_device_list(self, type):
        response = self.request('/dataservice/system/device/{0}'.format(type))

        if response.json:
            return response.json['data']
        else:
            return []

    def get_device_dict(self, type, key_name='host-name', remove_key=False):

        device_list = self.get_device_list(type)

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

    def get_device_status_list(self):
        response = self.request('/dataservice/device')

        if response.json:
            return response.json['data']
        else:
            return []

    def get_device_status_dict(self, key_name='host-name', remove_key=False):

        device_list = self.get_device_list()

        return self.list_to_dict(device_list, key_name=key_name, remove_key=remove_key)

    def get_device_vedges(self, key_name='host-name', remove_key=True):
        response = self.request('/dataservice/system/device/vedges')

        if response.json:
            return self.list_to_dict(response.json['data'], key_name=key_name, remove_key=remove_key)
        else:
            return {}

    def get_device_controllers(self, key_name='host-name', remove_key=True):
        response = self.request('/dataservice/system/device/controllers')

        if response.json:
            return self.list_to_dict(response.json['data'], key_name=key_name, remove_key=remove_key)
        else:
            return {}

    def create_controller(self, device_ip, personality, username, password):
        payload = {
            "deviceIP": device_ip,
            "username": username,
            "password": password,
            "personality": personality,
            "generateCSR": "false"
        }

        response = self.request('/dataservice/system/device', method='POST', payload=payload)

        if response.json:
            return response.json
        else:
            return None

    def delete_controller(self, uuid):
        response = self.request('/dataservice/certificate/{0}'.format(uuid), method='DELETE')

        return response

    def decommision_device(self, uuid):
        response = self.request('/dataservice/system/device/decommission/{0}'.format(uuid), method='PUT')

        return response

    def generate_csr(self, device_ip):
        payload = {"deviceIP": device_ip}
        response = self.request('/dataservice/certificate/generate/csr', method='POST', payload=payload)

        if response.json:
            try:
                return response.json['data'][0]['deviceCSR']
            except:
                return None
        else:
            return None

    def generate_bootstrap(self, uuid, version='v1'):
        if version == 'v2':
            response = self.request('/dataservice/system/device/bootstrap/device/{0}?configtype=cloudinit&inclDefRootCert=true&version=v2'.format(uuid))
        else:
            response = self.request('/dataservice/system/device/bootstrap/device/{0}?configtype=cloudinit'.format(uuid))

        try:
            bootstrap_config = response.json['bootstrapConfig']
        except:
            return None

        regex = re.compile(r'otp : (?P<otp>[a-z0-9]+)[^a-z0-9]')
        match = regex.search(bootstrap_config)
        if match:
            otp = match.groups('otp')[0]
        else:
            otp = None

        return_dict = {
            'bootstrapConfig': bootstrap_config,
            'otp': otp,
            'uuid': uuid
        }
        return return_dict

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
        response = self.request('/dataservice/template/device/config/input', method='POST', payload=payload)

        if response.json:
            if 'header' in response.json and 'columns' in response.json['header']:
                column_list = response.json['header']['columns']

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

    def get_template_variables(self, template_id):
        payload = {
            "deviceIds": [],
            "isEdited": False,
            "isMasterEdited": False,
            "templateId": template_id
        }
        return_dict = {}
        response = self.request('/dataservice/template/device/config/input', method='POST', payload=payload)

        if response.json:
            if 'header' in response.json and 'columns' in response.json['header']:
                column_list = response.json['header']['columns']

                regex = re.compile(r'\((?P<variable>[^(]+)\)')

                for column in column_list:
                    if column['editable']:
                        # match = regex.search(column['title'])
                        match = regex.findall(column['title'])
                        if match:
                            # variable = match.groups('variable')[0]
                            variable = match[-1]
                            return_dict[variable] = column['property']
                        else:
                            # Some variables don't have a variable name in the title, use property instead
                            return_dict[column['property']] = column['property']

        return return_dict

    def get_template_optional_variables(self, template_id):
        payload = {
            "deviceIds": [],
            "isEdited": False,
            "isMasterEdited": False,
            "templateId": template_id
        }
        return_dict = {}
        response = self.request('/dataservice/template/device/config/input', method='POST', payload=payload)

        if response.json:
            if 'header' in response.json and 'columns' in response.json['header']:
                column_list = response.json['header']['columns']

                regex = re.compile(r'\((?P<variable>[^(]+)\)')

                # The following can be removed once the API will mark as optional
                # the nexthop value of a static route that has been marked as optional
                regexYangStaticR = re.compile(r'.*/vpn-instance/ip/route/.*/prefix')
                regex_yang_nexthop = re.compile(r'.*/vpn-instance/ip/route/(?P<staticR>.*)/next-hop/.*/address')
                optionalStaticRoutesList = []
                # Until here

                # The following can be removed once the API will mark as optional
                # all the vrrp attributes once the vrrp grp-id has been marked optional
                regexYangVRRPgrpID = re.compile(r'.*/vrrp/.*/grp-id')
                regexYangVRRPpriority = re.compile(r'.*/vrrp/(?P<VVRPgrp>.*)/priority')
                regexYangVRRPtimer = re.compile(r'.*/vrrp/(?P<VVRPgrp>.*)/timer')
                regexYangVRRPtrackPrefix = re.compile(r'.*/vrrp/(?P<VVRPgrp>.*)/track-prefix-list')
                regexYangVRRPtrackOMP = re.compile(r'.*/vrrp/(?P<VVRPgrp>.*)/track-omp')
                regexYangVRRPipAddress = re.compile(r'.*/vrrp/(?P<VVRPgrp>.*)/ipv4/address')
                optionalVRRPvariales = []
                # Until here

                # The following can be removed once the API will mark as optional
                # all the logging attributes once the logging has been marked optional
                regexYangLoggingServerName = re.compile(r'///logging/server/.*/name')
                regexYangLoggingSourceInt = re.compile(r'///logging/server/(?P<LoggServer>.*)/source-interface')
                regexYangLoggingVPN = re.compile(r'///logging/server/(?P<LoggServer>.*)/vpn')
                regexYangLoggingPriority = re.compile(r'///logging/server/(?P<LoggServer>.*)/priority')
                optionalLoggingVariales = []
                # Until here

                for column in column_list:
                    # Skip this column if optional not found in dict
                    if 'optional' not in column:
                        continue

                    # The following can be removed once the API will mark as optional
                    # the nexthop value of a static route that has been marked as optional

                    # Based on the regular expression above we match
                    # static routes and next-hop variables based on the YANG variable
                    # a static route looks like this /1/vpn-instance/ip/route/<COMMON_NAME_OF_THE_ROUTE>/prefix
                    # a next-hop looks like this /1/vpn-instance/ip/route/<COMMON_NAME_OF_THE_ROUTE>/next-hop/<COMMON_NAME_OF_THE_NH>/address

                    # If we find a static route and this is optional we
                    # store its common name into an array
                    # we don't add this parameter to the return list now
                    # since it will be added later
                    isStaticR = regexYangStaticR.match(column['property'])
                    if isStaticR and column['optional']:
                        match = regex.findall(column['title'])
                        if match:
                            variable = match[-1]
                            optionalStaticRoutesList.append(variable)

                    # If we find a next-hop we extrapolate the common name
                    # of the static route. If we have already found that
                    # common name and we know it is optional we will add
                    # this next-hop paramter to the return list since it
                    # will be optional as well

                    # ALL OF THIS IS BASED ON THE ASSUMPTION THAT STATIC ROUTES
                    # ARE LISTED BEFORE NEXT-HOP VALUES
                    nextHopStaticR = regex_yang_nexthop.findall(column['property'])
                    if nextHopStaticR:
                        if nextHopStaticR[0] in optionalStaticRoutesList:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']

                    # Until here

                    # The following can be removed once the API will mark as optional
                    # the attributes for vrrp as optional if the whole vrrp has been
                    # marked as optional

                    # Based on the regular expression above we match
                    # vrrp atributes based on the YANG variable

                    # If we find a VRRP grp ID and this is optional we
                    # store its common name into an array
                    # we don't add this parameter to the return list now
                    # since it will be added later
                    isVRRP = regexYangVRRPgrpID.match(column['property'])
                    if isVRRP and column['optional']:
                        match = regex.findall(column['title'])
                        if match:
                            variable = match[-1]
                            optionalVRRPvariales.append(variable)

                    # If we find a any vrrp attribute we extrapolate the common name
                    # If we have already found that
                    # common name and we know it is optional we will add
                    # this paramter to the return list since it
                    # will be optional as well

                    # ALL OF THIS IS BASED ON THE ASSUMPTION THAT VRRP GRP-ID is
                    # LISTED BEFORE ALL THE OTHER ATTRIBUTES
                    VRRPpriority = regexYangVRRPpriority.findall(column['property'])
                    VRRPtimer = regexYangVRRPtimer.findall(column['property'])
                    VRRPtrackPrefix = regexYangVRRPtrackPrefix.findall(column['property'])
                    VRRPipAddress = regexYangVRRPipAddress.findall(column['property'])
                    VRRPtrackOMP = regexYangVRRPtrackOMP.findall(column['property'])
                    if VRRPpriority:
                        if VRRPpriority[0] in optionalVRRPvariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                    elif VRRPtimer:
                        if VRRPtimer[0] in optionalVRRPvariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                    elif VRRPtrackPrefix:
                        if VRRPtrackPrefix[0] in optionalVRRPvariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                    elif VRRPipAddress:
                        if VRRPipAddress[0] in optionalVRRPvariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                    elif VRRPtrackOMP:
                        if VRRPtrackOMP[0] in optionalVRRPvariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                                # Until here

                    # Same logic for logging optional variables
                    isLogging = regexYangLoggingServerName.match(column['property'])
                    if isLogging and column['optional']:
                        match = regex.findall(column['title'])
                        if match:
                            variable = match[-1]
                            optionalLoggingVariales.append(variable)

                    LoggingSourceInt = regexYangLoggingSourceInt.findall(column['property'])
                    LoggingVPN = regexYangLoggingVPN.findall(column['property'])
                    LoggingPriority = regexYangLoggingPriority.findall(column['property'])

                    if LoggingSourceInt:
                        if LoggingSourceInt[0] in optionalLoggingVariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                    elif LoggingVPN:
                        if LoggingVPN[0] in optionalLoggingVariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']
                    elif LoggingPriority:
                        if LoggingPriority[0] in optionalLoggingVariales:
                            match = regex.findall(column['title'])
                            if match:
                                variable = match[-1]
                                return_dict[variable] = column['property']

                    # Until here

                    if column['editable'] and column['optional']:
                        match = regex.findall(column['title'])
                        if match:
                            variable = match[-1]
                            return_dict[variable] = column['property']

        return return_dict

    def get_software_images_list(self):
        response = self.request('/dataservice/device/action/software', method='GET')

        if response.json:
            return response.json['data']
        else:
            return []

    def get_installed_software(self, type):
        response = self.request('/dataservice/device/action/install/devices/{0}?groupId=all'.format(type), method='GET')

        if response.json:
            return response.json['data']
        else:
            return []

    def software_install(self, devices, deviceType, data, reboot):

        payload = {
            "action": "install",
            "input": {
                "vEdgeVPN": 0,
                "vSmartVPN": 0,
                "data": data,
                "versionType": "vmanage",
                "reboot": reboot,
                "sync": True
            },
            "devices": devices,
            "deviceType": deviceType
        }

        response = self.request('/dataservice/device/action/install', method='POST', payload=payload)

        if response.json and 'id' in response.json:
            self.waitfor_action_completion(response.json['id'])
        else:
            self.fail_json(
                msg='Did not get action ID after installing software.')

        return response.json['id']

    def set_default_partition(self, devices, deviceType):

        payload = {
            "action": "defaultpartition",
            "devices": devices,
            "deviceType": deviceType
        }

        response = self.request('/dataservice/device/action/defaultpartition', method='POST', payload=payload)

        if response.json and 'id' in response.json:
            self.waitfor_action_completion(response.json['id'])
        else:
            self.fail_json(
                msg='Did not get action ID after setting default image.')

        return response.json['id']

    def push_certificates(self):
        response = self.request('/dataservice/certificate/vedge/list?action=push', method='POST')
        if response.json and 'id' in response.json:
            self.waitfor_action_completion(response.json['id'])
        else:
            self.fail_json(msg='Did not get action ID after pushing certificates.')
        return response.json['id']

    def reattach_device_template(self, template_id):
        device_list = self.get_template_attachments(template_id, key='uuid')
        # First, we need to get the input to feed to the re-attach
        payload = {
            "templateId": template_id,
            "deviceIds": device_list,
            "isEdited": "true",
            "isMasterEdited": "false"
        }
        response = self.request('/dataservice/template/device/config/input/', method='POST', payload=payload)
        # Then we feed that to the attach
        if response.json and 'data' in response.json:
            payload = {
                "deviceTemplateList":
                    [
                        {
                            "templateId": template_id,
                            "device": response.json['data'],
                            "isEdited": "true"
                        }
                    ]
            }
            response = self.request('/dataservice/template/device/config/attachfeature', method='POST', payload=payload)
            if response.json and 'id' in response.json:
                self.waitfor_action_completion(response.json['id'])
            else:
                self.fail_json(
                    msg='Did not get action ID after attaching device to template.')

            # if process_id:
            #    self.request('/dataservice/template/lock/{0}'.format(process_id), method='DELETE')

        else:
            self.fail_json(msg="Could not retrieve input for template {0}".format(template_id))
        return response.json['id']

    def waitfor_action_completion(self, action_id):
        status = 'in_progress'
        response = {}
        while status == "in_progress":
            response = self.request('/dataservice/device/action/status/{0}'.format(action_id))
            if response.json:
                status = response.json['summary']['status']
                if 'data' in response.json and response.json['data']:
                    action_status = response.json['data'][0]['statusId']
                    action_activity = response.json['data'][0]['activity']
                    if 'actionConfig' in response.json['data'][0]:
                        action_config = response.json['data'][0]['actionConfig']
                    else:
                        action_config = None
            else:
                self.fail_json(msg="Unable to get action status: No response")
            time.sleep(10)

        # self.result['action_response'] = response.json
        self.result['action_id'] = action_id
        self.result['action_status'] = action_status
        self.result['action_activity'] = action_activity
        self.result['action_config'] = action_config
        if self.result['action_status'] == 'failure':
            self.fail_json(msg="Action failed")
        return response

    def exit_json(self, **kwargs):
        # self.logout()
        """Custom written method to exit from module."""

        self.result.update(**kwargs)
        self.module.exit_json(**self.result)

    def fail_json(self, msg, **kwargs):
        # self.logout()
        """Custom written method to return info on failure."""

        self.result.update(**kwargs)
        self.module.fail_json(msg=msg, **self.result)
