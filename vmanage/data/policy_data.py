"""Cisco vManage Policy Methods.
"""

import dictdiffer
from vmanage.api.policy_lists import PolicyLists
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.api.local_policy import LocalPolicy
from vmanage.api.central_policy import CentralPolicy
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.security_policy import SecurityPolicy


class PolicyData(object):
    """Methods that deal with importing, exporting, and manipulating data from policies.

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
        self.security_policy = SecurityPolicy(self.session, self.host, self.port)

    #pylint: disable=unused-argument
    def import_policy_list_list(self, policy_list_list, push=False, update=False, check_mode=False, force=False):
        """Import a list of policyies lists into vManage.  Object Names are translated to IDs.

        Args:
            policy_list_list: A list of polcies
            push (bool): Whether to push a change out
            update (bool): Whether to update when the list exists
            check_mode (bool): Report what updates would happen, but don't update

        Returns:
            result (dict): All data associated with a response.

        """

        # Policy Lists
        diff = []
        policy_list_updates = []
        #pylint: disable=too-many-nested-blocks
        for policy_list in policy_list_list:
            policy_list_dict = self.policy_lists.get_policy_list_dict(policy_list['type'],
                                                                      remove_key=False,
                                                                      cache=False)
            if policy_list['name'] in policy_list_dict:
                existing_list = policy_list_dict[policy_list['name']]
                diff_ignore = set(
                    ['listId', 'referenceCount', 'references', 'owner', 'lastUpdated', 'activatedId', 'policyId', 'isActivatedByVsmart'])
                diff = list(dictdiffer.diff(existing_list, policy_list, ignore=diff_ignore))
                if diff:
                    policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
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
                                        obj = vmanage_device_templates.get_device_template_object(template_id)
                                        vmanage_device_templates.reattach_device_template(
                                            template_id, obj['configType'])
                            else:
                                raise Exception("Did not get a process id when updating policy list")
            else:
                diff = list(dictdiffer.diff({}, policy_list))
                policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
                if not check_mode:
                    self.policy_lists.add_policy_list(policy_list)

        return policy_list_updates

    def convert_list_name_to_id(self, name_list):
        """Convert policy list from names to IDs in object.

        Args:
            name_list (list): Object

        """
        if isinstance(name_list, dict):
            for key, value in list(name_list.items()):
                if key.endswith(
                        'List') and key != "signatureWhiteList" and key != "urlWhiteList" and key != "urlBlackList":
                    t = key[0:len(key) - 4]
                    policy_list = self.policy_lists.get_policy_list_by_name(value, policy_list_type=t)
                    if policy_list:
                        name_list[key] = policy_list['listId']
                    else:
                        raise Exception(f"Could not find id for list {value}, type {t}")
                elif key.endswith('Lists'):
                    t = key[0:len(key) - 5]
                    new_list = []
                    for list_name in value:
                        policy_list = self.policy_lists.get_policy_list_by_name(list_name, policy_list_type=t)
                        if policy_list:
                            list_id = policy_list['listId']
                            new_list.append(list_id)
                        else:
                            raise Exception(f"Could not find id for list {list_name}, type {t}")
                    name_list[key] = new_list
                elif key.endswith('Zone'):
                    if value == 'Self Zone':
                        name_list[key] = 'self'
                    policy_list = self.policy_lists.get_policy_list_by_name(value, 'zone')
                    if policy_list:
                        name_list[key] = policy_list['listId']
                    else:
                        raise Exception(f"Could not find id for list {value}, type zone")
                elif key == 'listName':
                    if 'listType' in name_list:
                        policy_list = self.policy_lists.get_policy_list_by_name(name_list['listName'],
                                                                                policy_list_type=name_list['listType'])
                    else:
                        raise Exception(f"Could not find type for list {name_list['listName']}")
                    if policy_list and 'listId' in policy_list:
                        name_list['ref'] = policy_list['listId']
                        name_list.pop('listName')
                        name_list.pop('listType')
                    else:
                        raise Exception(
                            f"Could not find id for list {name_list['listName']}, type {name_list['listType']}")
                elif key == 'className':
                    if 'classType' in name_list:
                        policy_list = self.policy_lists.get_policy_list_by_name(name_list['className'],
                                                                                policy_list_type=name_list['classType'])
                    else:
                        raise Exception(f"Could not find type for list {name_list['className']}")
                    if policy_list and 'listId' in policy_list:
                        name_list['class'] = policy_list['listId']
                        name_list.pop('className')
                        name_list.pop('classType')
                    else:
                        raise Exception(
                            f"Could not find id for list {name_list['className']}, type {name_list['classType']}")
                else:
                    self.convert_list_name_to_id(value)
        elif isinstance(name_list, list):
            for item in name_list:
                self.convert_list_name_to_id(item)

    def convert_list_id_to_name(self, id_list):
        """Convert policy list from IDs to names in object.

        Args:
            id_list (list): Object

        """
        if isinstance(id_list, dict):
            for key, value in list(id_list.items()):
                if key.endswith(
                        'List') and key != "signatureWhiteList" and key != "urlWhiteList" and key != "urlBlackList":
                    t = key[0:len(key) - 4]
                    val = value
                    if isinstance(value, list):
                        val = value[0]
                    policy_list = self.policy_lists.get_policy_list_by_id(val, policy_list_type=t)
                    if policy_list:
                        id_list[key] = policy_list['name']
                    else:
                        raise Exception(f"Could not find name for list id {val}, type {t}")
                elif key.endswith('Lists'):
                    t = key[0:len(key) - 5]
                    new_list = []
                    for list_id in value:
                        policy_list = self.policy_lists.get_policy_list_by_id(list_id, policy_list_type=t)
                        if policy_list:
                            list_name = policy_list['name']
                            new_list.append(list_name)
                        else:
                            raise Exception(f"Could not find name for list id {list_id}, type {t}")
                    id_list[key] = new_list
                elif key.endswith('Zone'):
                    if value == 'self':
                        id_list[key] = 'Self Zone'
                    else:
                        policy_list = self.policy_lists.get_policy_list_by_id(value, 'zone')
                        if policy_list:
                            id_list[key] = policy_list['name']
                        else:
                            raise Exception(f"Could not find name for list {value}, type zone")
                elif key == 'ref':
                    policy_list = self.policy_lists.get_policy_list_by_id(id_list['ref'])
                    if policy_list:
                        id_list['listName'] = policy_list['name']
                        id_list['listType'] = policy_list['type']
                        id_list.pop('ref')
                    else:
                        raise Exception(f"Could not find name for list {id_list['ref']}")
                elif key == 'class':
                    policy_list = self.policy_lists.get_policy_list_by_id(id_list['class'])
                    if policy_list:
                        id_list['className'] = policy_list['name']
                        id_list['classType'] = policy_list['type']
                        id_list.pop('class')
                    else:
                        raise Exception(f"Could not find name for list {id_list['class']}")
                else:
                    self.convert_list_id_to_name(value)
        elif isinstance(id_list, list):
            for item in id_list:
                self.convert_list_id_to_name(item)

    def convert_sequences_to_id(self, sequence_list):
        """Convert sequence entries from IDs to names in object.

        Args:
            sequence_list (list): Sequence list

        """
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

    def convert_definition_id_to_name(self, policy_definition):
        """Convert policy_definition from IDs to names in object.

        Args:
            policy_definition (list): Sequence list

        """
        if 'assembly' in policy_definition and policy_definition['assembly']:
            for assembly_item in policy_definition['assembly']:
                policy_definition_detail = self.policy_definitions.get_policy_definition(
                    assembly_item['type'].lower(), assembly_item['definitionId'])
                definition_id = assembly_item.pop('definitionId')
                if policy_definition_detail:
                    assembly_item['definitionName'] = policy_definition_detail['name']
                else:
                    raise Exception("Cannot find policy definition for {0}".format(definition_id))
                if 'entries' in assembly_item:
                    # Translate list IDs to names
                    self.convert_list_id_to_name(assembly_item['entries'])

    def convert_definition_name_to_id(self, policy_definition):
        """Convert policy_definition from names to IDs in object.

        Args:
            policy_definition (list): Sequence list

        """
        if 'assembly' in policy_definition and policy_definition['assembly']:
            for assembly_item in policy_definition['assembly']:
                if assembly_item['definitionName']:
                    definition_name = assembly_item.pop('definitionName')
                policy_definition_dict = self.policy_definitions.get_policy_definition_dict(assembly_item['type'])
                if definition_name in policy_definition_dict:
                    assembly_item['definitionId'] = policy_definition_dict[definition_name]['definitionId']
                else:
                    raise Exception("Cannot find policy definition {0}".format(definition_name))
                if 'entries' in assembly_item:
                    self.convert_list_name_to_id(assembly_item['entries'])

    def convert_policy_definition_to_name(self, policy_definition):
        """Convert policy_definition objects from IDs to names

        Args:
            policy_definition (list): Sequence list

        Returns:
            result (dict): The converted policy definition

        """
        converted_policy_definition = policy_definition
        if 'definition' in policy_definition:
            self.convert_list_id_to_name(policy_definition['definition'])
        if 'sequences' in policy_definition:
            self.convert_list_id_to_name(policy_definition['sequences'])
        if 'rules' in policy_definition:
            self.convert_list_id_to_name(policy_definition['rules'])

        return converted_policy_definition

    def convert_policy_definition_to_id(self, policy_definition):
        """Convert policy_definition objects from names to IDs

        Args:
            policy_definition (list): Sequence list

        Returns:
            result (dict): The converted policy definition

        """
        converted_policy_definition = policy_definition
        if 'definition' in policy_definition:
            self.convert_list_name_to_id(policy_definition['definition'])
        if 'sequences' in policy_definition:
            self.convert_list_name_to_id(policy_definition['sequences'])
        if 'rules' in policy_definition:
            self.convert_list_name_to_id(policy_definition['rules'])

        return converted_policy_definition

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
            definition_detail = self.policy_definitions.get_policy_definition(policy_definition['type'],
                                                                              policy_definition['definitionId'])
            converted_policy_definition = self.convert_policy_definition_to_name(definition_detail)
            export_definition_list.append(converted_policy_definition)

        return export_definition_list

    #pylint: disable=unused-argument
    def import_policy_definition_list(self,
                                      policy_definition_list,
                                      update=False,
                                      push=False,
                                      check_mode=False,
                                      force=False):
        """Import Policy Definitions into vManage.  Object names are converted to IDs.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """
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
                existing_definition = self.convert_policy_definition_to_name(policy_definition_dict[definition['name']])
                # Just check the things that we care about changing.
                diff_ignore = set([
                    'lastUpdated', 'definitionId', 'referenceCount', 'references', 'owner', 'isActivatedByVsmart',
                    'infoTag', 'activatedId'
                ])
                diff = list(dictdiffer.diff(existing_definition, payload, ignore=diff_ignore))
                if diff:
                    converted_definition = self.convert_policy_definition_to_id(definition)
                    policy_definition_updates.append({'name': converted_definition['name'], 'diff': diff})
                    if not check_mode and update:
                        self.policy_definitions.update_policy_definition(
                            converted_definition, policy_definition_dict[converted_definition['name']]['definitionId'])
                    policy_definition_updates.append({'name': converted_definition['name'], 'diff': diff})
            else:
                # Policy definition does not exist
                diff = list(dictdiffer.diff({}, payload))
                policy_definition_updates.append({'name': definition['name'], 'diff': diff})
                converted_definition = self.convert_policy_definition_to_id(definition)
                if not check_mode:
                    self.policy_definitions.add_policy_definition(converted_definition)

        return policy_definition_updates

    def convert_policy_to_name(self, policy_item):
        """Convert policy items from IDs to names

        Args:
            definition_type (string): Policy item

        Returns:
            response (dict): The converted policy item

        """
        if 'policyDefinition' in policy_item:
            converted_policy_item = policy_item
            self.convert_definition_id_to_name(converted_policy_item['policyDefinition'])
            return converted_policy_item
        return policy_item

    def convert_policy_to_id(self, policy_item):
        """Convert policy items from names IDs

        Args:
            definition_type (string): Policy item

        Returns:
            response (dict): The converted policy item

        """
        if 'policyDefinition' in policy_item:
            converted_policy_item = policy_item
            self.convert_definition_name_to_id(converted_policy_item['policyDefinition'])
            return converted_policy_item
        return policy_item

    def export_local_policy_list(self):
        """Export Local Policies from vManage.  Object IDs are converted to names.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """
        export_policy_list = []
        local_policy_list = self.local_policy.get_local_policy_list()
        for local_policy in local_policy_list:
            converted_policy_definition = self.convert_policy_to_name(local_policy)
            export_policy_list.append(converted_policy_definition)

        return export_policy_list

    #pylint: disable=unused-argument
    def import_local_policy_list(self, local_policy_list, update=False, push=False, check_mode=False, force=False):
        """Import Local Policies into vManage.  Object names are converted to IDs.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """
        local_policy_dict = self.local_policy.get_local_policy_dict(remove_key=False)
        diff = []
        local_policy_updates = []
        for local_policy in local_policy_list:
            payload = {'policyName': local_policy['policyName']}
            payload['policyDescription'] = local_policy['policyDescription']
            payload['policyType'] = local_policy['policyType']
            payload['policyDefinition'] = local_policy['policyDefinition']
            if payload['policyName'] in local_policy_dict:
                # A policy by that name already exists
                existing_policy = self.convert_policy_to_name(local_policy_dict[payload['policyName']])
                diff_ignore = set([
                    'lastUpdated', 'policyVersion', 'createdOn', 'references', 'isPolicyActivated', '@rid', 'policyId',
                    'createdBy', 'lastUpdatedBy', 'lastUpdatedOn', 'mastersAttached', 'policyDefinitionEdit',
                    'devicesAttached'
                ])
                diff = list(dictdiffer.diff(existing_policy, payload, ignore=diff_ignore))
                if diff:
                    local_policy_updates.append({'name': local_policy['policyName'], 'diff': diff})
                    if 'policyDefinition' in payload:
                        self.convert_definition_name_to_id(payload['policyDefinition'])
                    if not check_mode and update:
                        self.local_policy.update_local_policy(payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                local_policy_updates.append({'name': local_policy['policyName'], 'diff': diff})
                if 'policyDefinition' in payload:
                    # Convert list and definition names to template IDs
                    self.convert_definition_name_to_id(payload['policyDefinition'])
                if not check_mode:
                    self.local_policy.add_local_policy(payload)
        return local_policy_updates

    def export_central_policy_list(self):
        """Export Central Policies from vManage, converting IDs to names.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        export_policy_list = []
        central_policy_list = self.central_policy.get_central_policy_list()
        for central_policy in central_policy_list:
            converted_policy_definition = self.convert_policy_to_name(central_policy)
            export_policy_list.append(converted_policy_definition)

        return export_policy_list

    #pylint: disable=unused-argument
    def import_central_policy_list(self, central_policy_list, update=False, push=False, check_mode=False, force=False):
        """Import Central Policies into vManage.  Object names are converted to IDs.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """
        central_policy_dict = self.central_policy.get_central_policy_dict(remove_key=False)
        diff = []
        central_policy_updates = []
        for central_policy in central_policy_list:
            payload = {'policyName': central_policy['policyName']}
            payload['policyDescription'] = central_policy['policyDescription']
            payload['policyType'] = central_policy['policyType']
            payload['policyDefinition'] = central_policy['policyDefinition']
            if payload['policyName'] in central_policy_dict:
                # A policy by that name already exists
                existing_policy = self.convert_policy_to_name(central_policy_dict[payload['policyName']])
                diff_ignore = set([
                    'lastUpdated', 'policyVersion', 'createdOn', 'references', 'isPolicyActivated', '@rid', 'policyId',
                    'createdBy', 'lastUpdatedBy', 'lastUpdatedOn'
                ])
                diff = list(dictdiffer.diff(existing_policy, payload, ignore=diff_ignore))
                if diff:
                    central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})
                    # Convert list and definition names to template IDs
                    converted_payload = self.convert_policy_to_id(payload)
                    if not check_mode and update:
                        self.central_policy.update_central_policy(converted_payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})
                if not check_mode:
                    # Convert list and definition names to template IDs
                    converted_payload = self.convert_policy_to_id(payload)
                    self.central_policy.add_central_policy(converted_payload)
        return central_policy_updates

    def export_security_policy_list(self):
        """Export Security Policies from vManage, converting IDs to names.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        export_policy_list = []
        security_policy_list = self.security_policy.get_security_policy_list()
        for security_policy in security_policy_list:
            converted_policy_definition = self.convert_policy_to_name(security_policy)
            export_policy_list.append(converted_policy_definition)

        return export_policy_list

    def import_security_policy_list(self,
                                    security_policy_list,
                                    update=False,
                                    push=False,
                                    check_mode=False,
                                    force=False):
        """Import Security Policies into vManage.  Object names are converted to IDs.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """
        security_policy_dict = self.security_policy.get_security_policy_dict(remove_key=False)
        diff = []
        security_policy_updates = []
        for security_policy in security_policy_list:
            payload = {'policyName': security_policy['policyName']}
            payload['policyDescription'] = security_policy['policyDescription']
            payload['policyType'] = security_policy['policyType']
            payload['policyDefinition'] = security_policy['policyDefinition']
            if payload['policyName'] in security_policy_dict:
                # A policy by that name already exists
                existing_policy = self.convert_policy_to_name(security_policy_dict[payload['policyName']])
                diff_ignore = set([
                    'lastUpdated', 'policyVersion', 'createdOn', 'references', 'isPolicyActivated', '@rid', 'policyId',
                    'createdBy', 'lastUpdatedBy', 'lastUpdatedOn', 'policyDefinitionEdit', 'mastersAttached',
                    'devicesAttached', 'supportedDevices', 'virtualApplicationTemplates', 'policyUseCase'
                ])
                diff = list(dictdiffer.diff(existing_policy, payload, ignore=diff_ignore))
                if diff:
                    security_policy_updates.append({'name': security_policy['policyName'], 'diff': diff})
                    # Convert list and definition names to template IDs
                    converted_payload = self.convert_policy_to_id(payload)
                    if not check_mode and update:
                        self.security_policy.update_security_policy(converted_payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                security_policy_updates.append({'name': security_policy['policyName'], 'diff': diff})
                if not check_mode:
                    # Convert list and definition names to template IDs
                    converted_payload = self.convert_policy_to_id(payload)
                    self.security_policy.add_security_policy(converted_payload)
        return security_policy_updates
