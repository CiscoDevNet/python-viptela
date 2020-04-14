"""Cisco vManage Policy Definitions API Methods.
"""

import json

import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.api.policy_lists import PolicyLists
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


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

    def convert_list_id_to_name(self, id_list):
        if isinstance(id_list, dict):
            for key, value in list(id_list.items()):
                if key.endswith('List'):
                    t = key[0:len(key) - 4]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(t, key_name='listId')
                    if value in policy_list_dict:
                        id_list[key] = policy_list_dict[value]['name']
                elif key.endswith('Lists'):
                    t = key[0:len(key) - 5]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(t, key_name='listId')
                    new_list = []
                    for list_id in value:
                        if list_id in policy_list_dict:
                            list_name = policy_list_dict[list_id]['name']
                            new_list.append(list_name)
                        else:
                            new_list.append(list_id)
                    id_list[key] = new_list
                elif key.endswith('Zone'):
                    policy_list_dict = self.policy_lists.get_policy_list_dict('zone', key_name='listId')
                    if value in policy_list_dict:
                        id_list[key] = policy_list_dict[value]['name']
                elif key == 'ref':
                    policy_list_dict = self.policy_lists.get_policy_list_dict('all', key_name='listId')
                    if id_list['ref'] in policy_list_dict:
                        id_list['listName'] = policy_list_dict[id_list['ref']]['name']
                        id_list['listType'] = policy_list_dict[id_list['ref']]['type']
                        id_list.pop('ref')
                    else:
                        raise Exception("Could not find list {0}".format(id_list['ref']))
                elif key == 'class':
                    policy_list_dict = self.policy_lists.get_policy_list_dict('all', key_name='listId')
                    if id_list['class'] in policy_list_dict:
                        id_list['className'] = policy_list_dict[id_list['class']]['name']
                        id_list['classType'] = policy_list_dict[id_list['class']]['type']
                        id_list.pop('class')
                    else:
                        raise Exception("Could not find list {0}".format(id_list['ref']))
                else:
                    self.convert_list_id_to_name(value)
        elif isinstance(id_list, list):
            for item in id_list:
                self.convert_list_id_to_name(item)

    def convert_list_name_to_id(self, name_list):
        if isinstance(name_list, dict):
            for key, value in list(name_list.items()):
                if key.endswith('List'):
                    t = key[0:len(key) - 4]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(t)
                    if value in policy_list_dict:
                        name_list[key] = policy_list_dict[value]['listId']
                elif key.endswith('Lists'):
                    t = key[0:len(key) - 5]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(t)
                    new_list = []
                    for list_name in value:
                        if list_name in policy_list_dict:
                            list_id = policy_list_dict[list_name]['listId']
                            new_list.append(list_id)
                        else:
                            new_list.append(list_name)
                    name_list[key] = new_list
                elif key.endswith('Zone'):
                    policy_list_dict = self.policy_lists.get_policy_list_dict('zone')
                    if value in policy_list_dict:
                        name_list[key] = policy_list_dict[value]['listId']
                elif key == 'listName':
                    if 'listType' in name_list:
                        policy_list_dict = self.policy_lists.get_policy_list_dict(name_list['listType'],
                                                                                  key_name='name')
                    else:
                        raise Exception("Could not find type for list {0}".format(name_list['listName']))
                    if name_list['listName'] in policy_list_dict and 'listId' in policy_list_dict[
                            name_list['listName']]:
                        name_list['ref'] = policy_list_dict[name_list['listName']]['listId']
                        name_list.pop('listName')
                        name_list.pop('listType')
                    else:
                        raise Exception("Could not find id for list {0}, type {1}".format(
                            name_list['listName'], name_list['listType']))
                elif key == 'className':
                    if 'classType' in name_list:
                        policy_list_dict = self.policy_lists.get_policy_list_dict(name_list['classType'],
                                                                                  key_name='name')
                    else:
                        raise Exception("Could not find type for list {0}".format(name_list['className']))
                    if name_list['className'] in policy_list_dict and 'listId' in policy_list_dict[
                            name_list['className']]:
                        name_list['class'] = policy_list_dict[name_list['className']]['listId']
                        name_list.pop('className')
                        name_list.pop('classType')
                    else:
                        raise Exception("Could not find id for list {0}, type {1}".format(
                            name_list['listName'], name_list['listType']))
                else:
                    self.convert_list_name_to_id(value)
        elif isinstance(name_list, list):
            for item in name_list:
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
        HttpMethods(self.session, url).request('GET')

    def add_policy_definition(self, policy_definition):
        """Delete a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{policy_definition['type'].lower()}"
        HttpMethods(self.session, url).request('POST', payload=json.dumps(policy_definition))

    def update_policy_definition(self, policy_definition, policy_definition_id):
        """Update a Policy Definition from vManage.

        Args:
            definition_type (str): The defintion type of the requested policy definition
            definition_id (str): The defintion ID of the requested policy definition

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/definition/{policy_definition['type'].lower()}/{policy_definition_id}"
        HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy_definition))

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
            for def_type in definition_type_titles:
                definition_list_types.append(def_type['key'].lower())
            for def_type in definition_list_types:
                definition_list = self.get_policy_definition_list(def_type)
                if definition_list:
                    all_definitions_list.extend(definition_list)
            return all_definitions_list

        definition_list = []

        url = f"{self.base_url}template/policy/definition/{definition_type.lower()}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        for definition in result:
            definition_detail = self.get_policy_definition(definition_type, definition['definitionId'])
            if definition_detail:
                definition_list.append(definition_detail)
        return definition_list

    def get_policy_definition_dict(self, t, key_name='name', remove_key=False):
        policy_definition_list = self.get_policy_definition_list(t)
        return list_to_dict(policy_definition_list, key_name, remove_key=remove_key)

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

    #pylint: disable=unused-argument
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
                        self.update_policy_definition(definition,
                                                      policy_definition_dict[definition['name']]['definitionId'])
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
                    self.add_policy_definition(definition)

        return policy_definition_updates
