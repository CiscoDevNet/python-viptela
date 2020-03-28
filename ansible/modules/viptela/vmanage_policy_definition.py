#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import os
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela import viptelaModule, viptela_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    # we only support the 'data' type currently, it will be fixed when we migrate to the SDK
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         aggregate=dict(type='list'),
                         name=dict(type='str'),
                         description = dict(type = 'str'),
                         type = dict(type ='str', required = False, choices= ['data']),
                         sequences = dict(type ='list'),
                         default_action = dict(type ='dict', alias='defaultAction'),
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

    # Always as an aggregate... make a definition if just given a single entry
    if viptela.params['aggregate']:
        definition_list = viptela.params['aggregate']
    else:
        definition_list = [
            {
                "name": viptela.params['name'],
                "description": viptela.params['description'],
                "type": viptela.params['type'],
                "sequences": viptela.params['sequences'],
                "defaultAction": viptela.params['default_action']
            }
        ]

    compare_values = ["name", "description", "type", "sequences", "defaultAction"]

    # Import site lists
    for definition in definition_list:
        policy_definition_dict = viptela.get_policy_definition_dict(definition['type'].lower(), remove_key=False)
        # payload = {
        #     "name": definition['name'],
        #     "description": definition['description'],
        #     "type": definition['type']
        # }
        # if 'sequences' in definition:
        #     payload['sequences'] = definition['sequences']
        # if 'defaultAction' in definition:
        #     payload['defaultAction'] = definition['defaultAction']    

        if viptela.params['state'] == 'present':
            if definition['name'] in policy_definition_dict:
                changed_items = viptela.compare_payloads(definition, policy_definition_dict[definition['name']], compare_values=compare_values)
                if changed_items:
                    viptela.result['changed'] = True
                    viptela.result['what_changed'] = changed_items
                    if 'sequences' in definition:
                        definition['sequences'] = viptela.convert_sequences_to_id(definition['sequences'])
                    if not module.check_mode:
                        viptela.request('/dataservice/template/policy/definition/{0}/{1}'.format(definition['type'].lower(), policy_definition_dict[definition['name']]['definitionId']),
                                        method='PUT', payload=definition)
            else:
                if 'sequences' in definition:
                    definition['sequences'] = viptela.convert_sequences_to_id(definition['sequences'])
                if not module.check_mode:
                    viptela.request('/dataservice/template/policy/definition/{0}/'.format(definition['type']).lower(),
                                    method='POST', payload=definition)
                viptela.result['changed'] = True
        else:
            if definition['name'] in policy_definition_dict:
                if not module.check_mode:
                    viptela.request('/dataservice/template/policy/definition/{0}/{1}'.format(definition['type'].lower(), definition['definitionId']),
                                    method='DELETE')
                viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)

def main():
    run_module()

if __name__ == '__main__':
    main()