"""Cisco vManage Policy Methods.
"""

import dictdiffer
from vmanage.api.policy_lists import PolicyLists
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.api.local_policy import LocalPolicy
from vmanage.api.central_policy import CentralPolicy
from vmanage.api.device_templates import DeviceTemplates


class PolicyData(object):
    """vManage Policy Methods

    Responsible vManage Policy.

    """
    def __init__(self, session, host, port=443):
        """Initialize Policy Method object with session parameters.

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
        self.policy_definitions = PolicyDefinitions(self.session, self.host, self.port)
        self.local_policy = LocalPolicy(self.session, self.host, self.port)
        self.central_policy = CentralPolicy(self.session, self.host, self.port)

    #pylint: disable=unused-argument
    def import_policy_list_list(self, policy_list_list, push=False, update=False, check_mode=False, force=False):
        """Import a list of policy lists into vManage

        Args:
            policy_list_list: A list of polcies
            push (bool): Whether to push a change out
            update (bool): Whether to update when the list exists
            check_mode (bool): Report what updates would happen, but don't update

        Returns:
            result (dict): All data associated with a response.

        """

        # Policy Lists
        policy_list_updates = []
        #pylint: disable=too-many-nested-blocks
        for policy_list in policy_list_list:
            policy_list_dict = self.policy_lists.get_policy_list_dict(policy_list['type'],
                                                                      remove_key=False,
                                                                      cache=False)
            if policy_list['name'] in policy_list_dict:
                existing_list = policy_list_dict[policy_list['name']]
                diff = list(dictdiffer.diff(existing_list['entries'], policy_list['entries']))
                if diff:
                    policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
                if diff:
                    policy_list['listId'] = policy_list_dict[policy_list['name']]['listId']
                    # If description is not specified, try to get it from the existing information
                    if not policy_list['description']:
                        policy_list['description'] = policy_list_dict[policy_list['name']]['description']
                    if not check_mode and update:
                        response = self.policy_lists.update_policy_list(policy_list)

                        if response['json']:
                            # Updating the policy list returns a `processId` that locks the list and 'masterTemplatesAffected'
                            # that lists the templates affected by the change.
                            if 'error' in response['json']:
                                raise Exception(response['json']['error']['message'])
                            elif 'processId' in response['json']:
                                if push:
                                    vmanage_device_templates = DeviceTemplates(self.session, self.host)
                                    # If told to push out the change, we need to reattach each template affected by the change
                                    for template_id in response['json']['masterTemplatesAffected']:
                                        vmanage_device_templates.reattach_device_template(template_id)
                            else:
                                raise Exception("Did not get a process id when updating policy list")
            else:
                diff = list(dictdiffer.diff({}, policy_list))
                policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
                if not check_mode:
                    self.policy_lists.add_policy_list(policy_list)

        return policy_list_updates

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

    def convert_list_id_to_name(self, id_list):
        if isinstance(id_list, dict):
            for key, value in list(id_list.items()):
                if key.endswith('List'):
                    t = key[0:len(key) - 4]
                    policy_list_dict = self.policy_lists.get_policy_list_dict(t, key_name='listId')
                    val = value
                    if isinstance(value, list):
                        val = value[0]
                    if val in policy_list_dict:
                        id_list[key] = policy_list_dict[val]['name']
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

    def convert_definition_id_to_name(self, policy_definition):
        if 'assembly' in policy_definition and policy_definition['assembly']:
            for assembly_item in policy_definition['assembly']:
                policy_definition_detail = self.policy_definitions.get_policy_definition(assembly_item['type'].lower(),
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
        if 'assembly' in policy_definition and policy_definition['assembly']:
            for assembly_item in policy_definition['assembly']:
                definition_name = assembly_item.pop('definitionName')
                policy_definition_dict = self.policy_definitions.get_policy_definition_dict(assembly_item['type'])
                if definition_name in policy_definition_dict:
                    assembly_item['definitionId'] = policy_definition_dict[definition_name]['definitionId']
                else:
                    raise Exception("Cannot find policy definition {0}".format(definition_name))
                if 'entries' in assembly_item:
                    self.convert_list_name_to_id(assembly_item['entries'])

    def export_policy_definition_list(self, definition_type='all'):
        """Export Policy Definition Lists from vManage, translating IDs to Names.

        Args:
            definition_type (string): The type of Definition List to retreive

        Returns:
            response (list): A list of all definition lists currently
                in vManage.

        """

        policy_definition_list = self.policy_definitions.get_policy_definition_list(definition_type)
        export_definition_list = []
        for policy_definition in policy_definition_list:
            definition_detail = self.policy_definitions.get_policy_definition(policy_definition['type'], policy_definition['definitionId'])
            if definition_detail:
                if 'definition' in definition_detail:
                    self.convert_list_id_to_name(definition_detail['definition'])
                if 'sequences' in definition_detail:
                    self.convert_list_id_to_name(definition_detail['sequences'])
                if 'rules' in definition_detail:
                    self.convert_list_id_to_name(definition_detail['rules'])
                export_definition_list.append(definition_detail)

        return export_definition_list

    #pylint: disable=unused-argument
    def import_policy_definition_list(self,
                                      policy_definition_list,
                                      update=False,
                                      push=False,
                                      check_mode=False,
                                      force=False):
        policy_definition_updates = []
        for definition in policy_definition_list:
            policy_definition_dict = self.policy_definitions.get_policy_definition_dict(definition['type'],
                                                                                        remove_key=False)
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
                        self.policy_definitions.update_policy_definition(
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
                    self.policy_definitions.add_policy_definition(definition)

        return policy_definition_updates

    def export_local_policy_list(self):
        """Export all Central Policies from vManage.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        local_policy_list = self.local_policy.get_local_policy_list()
        for policy in local_policy_list:
            self.convert_definition_id_to_name(policy['policyDefinition'])
        return local_policy_list

    #pylint: disable=unused-argument
    def import_local_policy_list(self, local_policy_list, update=False, push=False, check_mode=False, force=False):
        local_policy_dict = self.local_policy.get_local_policy_dict(remove_key=False)
        local_policy_updates = []
        for local_policy in local_policy_list:
            payload = {'policyName': local_policy['policyName']}
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
                        self.local_policy.update_local_policy(payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                if 'policyDefinition' in payload:
                    # Convert list and definition names to template IDs
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode:
                    self.local_policy.add_local_policy(payload)
        return local_policy_updates

    def export_central_policy_list(self):
        """Export Central Policies from vManage, converting IDs to names

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        central_policy_list = self.central_policy.get_central_policy_list()
        # We need to convert the policy definitions from JSON
        for policy in central_policy_list:
            self.convert_definition_id_to_name(policy['policyDefinition'])
        return central_policy_list

    #pylint: disable=unused-argument
    def import_central_policy_list(self, central_policy_list, update=False, push=False, check_mode=False, force=False):
        central_policy_dict = self.central_policy.get_central_policy_dict(remove_key=True)
        central_policy_updates = []
        for central_policy in central_policy_list:
            payload = {'policyName': central_policy['policyName']}
            payload['policyDescription'] = central_policy['policyDescription']
            payload['policyType'] = central_policy['policyType']
            payload['policyDefinition'] = central_policy['policyDefinition']
            if payload['policyName'] in central_policy_dict:
                # A policy by that name already exists
                existing_policy = central_policy_dict[payload['policyName']]
                diff = list(dictdiffer.diff(existing_policy['policyDefinition'], payload['policyDefinition']))
                if diff:
                    central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})
                if len(diff):
                    # Convert list and definition names to template IDs
                    if 'policyDefinition' in payload:
                        self.convert_definition_name_to_id(payload['policyDefinition'])
                    if not check_mode and update:
                        self.central_policy.update_central_policy(payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})
                if not check_mode:
                    # Convert list and definition names to template IDs
                    if 'policyDefinition' in payload:
                        self.convert_definition_name_to_id(payload['policyDefinition'])
                    self.central_policy.add_central_policy(payload)
        return central_policy_updates
