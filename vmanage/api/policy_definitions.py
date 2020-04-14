"""Cisco vManage Policy Definitions API Methods.
"""

import json
import requests
import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.api.policy_lists import PolicyLists


class PolicyDefinitions(object):
    """vManage Policy Definitions API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Policy Definitions used in Centralized, Localized, and Security Policy.

    """
    def __init__(self, session, host, port=443):
        """Initialize Policy Lists object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.policy_lists = PolicyLists(self.session, self.host, self.port)

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

    def convert_list_id_to_name(self, input):
        if isinstance(input, dict):
            for key, value in list(input.items()):
                if key.endswith('List'):
                    type = key[0:len(key) - 4]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(type, key_name='listId')
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['name']
                elif key.endswith('Lists'):
                    type = key[0:len(key) - 5]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(type, key_name='listId')
                    new_list = []
                    for list_id in value:
                        if list_id in policy_list_dict:
                            list_name = policy_list_dict[list_id]['name']
                            new_list.append(list_name)
                        else:
                            new_list.append(list_id)
                    input[key] = new_list
                elif key.endswith('Zone'):
                    policy_list_dict = self.policy_lists.get_policy_list_dict('zone', key_name='listId')
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['name']
                elif key == 'ref':
                    policy_list_dict = self.policy_lists.get_policy_list_dict('all', key_name='listId')
                    if input['ref'] in policy_list_dict:
                        input['listName'] = policy_list_dict[input['ref']]['name']
                        input['listType'] = policy_list_dict[input['ref']]['type']
                        input.pop('ref')
                    else:
                        raise Exception("Could not find list {0}".format(input['ref']))
                elif key == 'class':
                    policy_list_dict = self.policy_lists.get_policy_list_dict('all', key_name='listId')
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
                    type = key[0:len(key) - 4]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(type)
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['listId']
                elif key.endswith('Lists'):
                    type = key[0:len(key) - 5]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(type)
                    new_list = []
                    for list_name in value:
                        if list_name in policy_list_dict:
                            list_id = policy_list_dict[list_name]['listId']
                            new_list.append(list_id)
                        else:
                            new_list.append(list_name)
                    input[key] = new_list
                elif key.endswith('Zone'):
                    policy_list_dict = self.policy_lists.get_policy_list_dict('zone')
                    if value in policy_list_dict:
                        input[key] = policy_list_dict[value]['listId']
                elif key == 'listName':
                    if 'listType' in input:
                        policy_list_dict = self.policy_lists.get_policy_list_dict(input['listType'], key_name='name')
                    else:
                        raise Exception("Could not find type for list {0}".format(input['listName']))
                    if input['listName'] in policy_list_dict and 'listId' in policy_list_dict[input['listName']]:
                        input['ref'] = policy_list_dict[input['listName']]['listId']
                        input.pop('listName')
                        input.pop('listType')
                    else:
                        raise Exception("Could not find id for list {0}, type {1}".format(
                            input['listName'], input['listType']))
                elif key == 'className':
                    if 'classType' in input:
                        policy_list_dict = self.policy_lists.get_policy_list_dict(input['classType'], key_name='name')
                    else:
                        raise Exception("Could not find type for list {0}".format(input['className']))
                    if input['className'] in policy_list_dict and 'listId' in policy_list_dict[input['className']]:
                        input['class'] = policy_list_dict[input['className']]['listId']
                        input.pop('className')
                        input.pop('classType')
                    else:
                        raise Exception("Could not find id for list {0}, type {1}".format(
                            input['listName'], input['listType']))
                else:
                    self.convert_list_name_to_id(value)
        elif isinstance(input, list):
            for item in input:
                self.convert_list_name_to_id(item)

    def convert_definition_id_to_name(self, policy_definition):
        if 'assembly' in policy_definition:
            for assembly_item in policy_definition['assembly']:
                policy_definition_detail = self.get_policy_definition(assembly_item['type'].lower(),
                                                                      assembly_item['definitionId'])
                definition_id = assembly_item.pop('definitionId')
                if policy_definition_detail:
                    assembly_item['definitionName'] = policy_definition_detail['name']
                else:
                    raise Exception("Cannot find policy definition for {0}".format(definition_id))
                if 'entries' in assembly_item:
                    # Translate list IDs to names
                    self.convert_list_id_to_name(assembly_item['entries'])

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

    def delete_policy_definition(self, definition_type, definition_id):
        """Delete a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{definition_type.lower()}/{definition_id}"
        response = HttpMethods(self.session, url).request('GET')

    def add_policy_definition(self, policy_definition):
        """Delete a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{policy_definition['type'].lower()}"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(policy_definition))

    def update_policy_definition(self, policy_definition, policy_definition_id):
        """Update a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{policy_definition['type'].lower()}/{policy_definition_id}"
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy_definition))

    def get_policy_definition(self, definition_type, definition_id):
        """Get a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        api = 'template/policy/definition/{0}/{1}'.format(definition_type.lower(), definition_id)
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')

        policy_definition = response["json"]
        if 'definition' in policy_definition:
            self.convert_list_id_to_name(policy_definition['definition'])
        if 'sequences' in policy_definition:
            self.convert_list_id_to_name(policy_definition['sequences'])
        if 'rules' in policy_definition:
            self.convert_list_id_to_name(policy_definition['rules'])
        return policy_definition

    def get_policy_definition_list(self, definition_type='all'):
        """Get all Policy Definition Lists from vManage.

        Args:
            definition_type (string): The type of Definition List to retreive

        Returns:
            response (dict): A list of all definition lists currently
                in vManage.

        """

        if definition_type == 'all':
            # Get a list of hub-and-spoke because it tells us the other definition types
            # known by this server (hopefully) in the header section
            all_definitions_list = []
            definition_list_types = []
            api = "template/policy/definition/hubandspoke"
            url = self.base_url + api
            response = HttpMethods(self.session, url).request('GET')

            try:
                definition_type_titles = response['json']['header']['columns'][1]['keyvalue']
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
            policy_list_dict = self.policy_lists.get_policy_list_dict('all', key_name='listId')

            url = f"{self.base_url}template/policy/definition/{definition_type.lower()}"
            response = HttpMethods(self.session, url).request('GET')
            result = ParseMethods.parse_data(response)
            for definition in result:
                definition_detail = self.get_policy_definition(definition_type, definition['definitionId'])
                if definition_detail:
                    definition_list.append(definition_detail)
            return definition_list

    def get_policy_definition_dict(self, type, key_name='name', remove_key=False):
        policy_definition_list = self.get_policy_definition_list(type)
        return self.list_to_dict(policy_definition_list, key_name, remove_key=remove_key)

    def convert_sequences_to_id(self, sequence_list):
        for sequence in sequence_list:
            if 'match' in sequence and 'entries' in sequence['match']:
                for entry in sequence['match']['entries']:
                    if 'listName' in entry:
                        policy_list_dict = self.policy_lists.get_policy_list_dict(entry['listType'])
                        if entry['listName'] in policy_list_dict:
                            entry['ref'] = policy_list_dict[entry['listName']]['listId']
                            entry.pop('listName')
                            entry.pop('listType')
                        else:
                            raise Exception("Could not find list {0} of type {1}".format(
                                entry['listName'], entry['listType']))

    def import_policy_definition_list(self,
                                      policy_definition_list,
                                      update=False,
                                      push=False,
                                      check_mode=False,
                                      force=False):
        policy_definition_updates = []
        for definition in policy_definition_list:
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
                        response = self.update_policy_definition(
                            definition, policy_definition_dict[definition['name']]['definitionId'])
                    policy_definition_updates.append({'name': definition['name'], 'diff': diff})
            else:
                diff = list(dictdiffer.diff({}, payload))
                policy_definition_updates.append({'name': definition['name'], 'diff': diff})
                # List does not exist
                if 'definition' in definition:
                    self.convert_list_name_to_id(definition['definition'])
                if 'sequences' in definition:
                    self.convert_list_name_to_id(definition['sequences'])
                if 'rules' in definition:
                    self.convert_list_name_to_id(definition['rules'])
                if not check_mode:
                    response = self.add_policy_definition(definition)

        return policy_definition_updates
