#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela import viptelaModule, viptela_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present', 'activated', 'deactivated'], default='present'),
                         name = dict(type='str', alias='policyName'),
                         description = dict(type='str', alias='policyDescription'),
                         definition = dict(type='str', alias='policyDefinition'),
                         type = dict(type='list', alias='policyType'),
                         wait = dict(type='bool', default=False),
                         aggregate=dict(type='list'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )
    viptela = viptelaModule(module)

    # Always as an aggregate... make a list if just given a single entry
    if viptela.params['aggregate']:
        policy_list =  viptela.params['aggregate']
    else:
        if viptela.params['state'] == 'present':
            policy_list = [
                {
                    'policyName': viptela.params['name'],
                    'policyDescription': viptela.params['description'],
                    'policyType': viptela.params['type'],
                    'policyDefinition': viptela.params['definition'],
                }
            ]
        else:
            policy_list = [
                {
                    'policyName': viptela.params['name'],
                    'state': 'absent'
                }
            ]

    central_policy_dict = viptela.get_central_policy_dict(remove_key=False)

    compare_values = ['policyName', 'policyDescription', 'policyType', 'policyDefinition']
    ignore_values = ["lastUpdatedOn", "lastUpdatedBy", "templateId", "createdOn", "createdBy"]

    for policy in policy_list:
        payload = {
            'policyName': policy['policyName']
        }
        if viptela.params['state'] == 'present':
            payload['policyDescription'] = policy['policyDescription']
            payload['policyType'] = policy['policyType']
            payload['policyDefinition'] = policy['policyDefinition']
            # If a template by that name is already there
            if payload['policyName'] in central_policy_dict:
                viptela.result['changed'] = False
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
                if not module.check_mode:
                    #
                    # Convert list and definition names to template IDs
                    #
                    regex = re.compile(r'^(?P<type>.*)Lists$')
                    for policy_item in policy['policyDefinition']['assembly']:
                        definition_name = policy_item.pop('definitionName')
                        policy_definition_dict = viptela.get_policy_definition_dict(policy_item['type'])
                        if definition_name in policy_definition_dict:
                            policy_item['definitionId'] = policy_definition_dict[definition_name]['definitionId']
                        else:
                            viptela.fail_json(msg="Cannot find policy definition {0}".format(definition_name))
                        for entry in policy_item['entries']:
                            for list_type, list in entry.items():
                                match = regex.search(list_type)
                                if match:
                                    type = match.groups('type')[0]
                                    if type in viptela.POLICY_LIST_TYPES:
                                        policy_list_dict = viptela.get_policy_list_dict(type)
                                        for index, list_name in enumerate(list):
                                            list[index] = policy_list_dict[list_name]['listId']
                                    else:
                                        viptela.fail_json(msg="Cannot find list type {0}".format(type))

                    viptela.request('/dataservice/template/policy/vsmart', method='POST', payload=payload)
                    viptela.result['payload'] = payload
                    viptela.result['changed'] = True
        elif viptela.params['state'] == 'activated':
            if policy['policyName'] in central_policy_dict:
                if not central_policy_dict[policy['policyName']]['isPolicyActivated']:
                    viptela.result['changed'] = True
                    if not module.check_mode:
                        response = viptela.request('/dataservice/template/policy/vsmart/activate/{0}'.format(central_policy_dict[policy['policyName']]['policyId']),
                                        method='POST', payload=payload)
                        if response.json:
                            action_id = response.json['id']
                        else:
                            viptela.fail_json(msg='Did not get action ID after attaching device to template.')
                        if viptela.params['wait']:
                            viptela.waitfor_action_completion(action_id)
            else:
                viptela.fail_json(msg="Cannot find central policy {0}".format(policy['policyName']))
        if viptela.params['state'] in ['absent', 'deactivated']:
            if policy['policyName'] in central_policy_dict:
                if central_policy_dict[policy['policyName']]['isPolicyActivated']:
                    viptela.result['changed'] = True
                    if not module.check_mode:
                        response = viptela.request('/dataservice/template/policy/vsmart/deactivate/{0}'.format(central_policy_dict[policy['policyName']]['policyId']),
                                        method='POST')
                        if response.json:
                            action_id = response.json['id']
                        else:
                            viptela.fail_json(msg='Did not get action ID after attaching device to template.')
                        if viptela.params['wait']:
                            viptela.waitfor_action_completion(action_id)
            else:
                viptela.fail_json(msg="Cannot find central policy {0}".format(policy['policyName']))
        elif viptela.params['state'] == 'absent':
            if device_template['templateName'] in device_template_dict:
                if not module.check_mode:
                    viptela.request('/dataservice/template/policy/vsmart/{0}'.format(central_policy_dict[policy[policyName]]['policyId']),
                                    method='DELETE')
                viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)

def main():
    run_module()

if __name__ == '__main__':
    main()