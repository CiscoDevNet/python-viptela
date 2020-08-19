#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.central_policy import CentralPolicy
from vmanage.data.policy_data import PolicyData
from vmanage.api.utilities import Utilities


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present', 'activated', 'deactivated'], default='present'),
                         name=dict(type='str', alias='policyName'),
                         description=dict(type='str', alias='policyDescription'),
                         definition=dict(type='str', alias='policyDefinition'),
                         type=dict(type='list', alias='policyType'),
                         wait=dict(type='bool', default=False),
                         update=dict(type='bool', default=False),
                         push=dict(type='bool', default=False),
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
    vmanage = Vmanage(module)
    vmanage_central_policy = CentralPolicy(vmanage.auth, vmanage.host)
    policy_data = PolicyData(vmanage.auth, vmanage.host)
    vmanage_utils = Utilities(vmanage.auth, vmanage.host)

    # Always as an aggregate... make a list if just given a single entry
    if vmanage.params['aggregate']:
        policy_list = vmanage.params['aggregate']
    else:
        if vmanage.params['state'] == 'present':
            policy_list = [
                {
                    'policyName': vmanage.params['name'],
                    'policyDescription': vmanage.params['description'],
                    'policyType': vmanage.params['type'],
                    'policyDefinition': vmanage.params['definition'],
                }
            ]
        else:
            policy_list = [
                {
                    'policyName': vmanage.params['name'],
                    'state': 'absent'
                }
            ]

    central_policy_updates = []
    if vmanage.params['state'] == 'present':
        central_policy_updates = policy_data.import_central_policy_list(
            policy_list,
            check_mode=module.check_mode,
            update=vmanage.params['update'],
            push=vmanage.params['push']
        )
        if central_policy_updates:
            vmanage.result['changed'] = True
    elif vmanage.params['state'] == 'absent':
        central_policy_dict = vmanage_central_policy.get_central_policy_dict(remove_key=False)
        for policy in policy_list:
            if policy in central_policy_dict:
                if not module.check_mode:
                    vmanage_central_policy.delete_central_policy(central_policy_dict[policy['policyName']]['policyId'])
                vmanage.result['changed'] = True
    elif vmanage.params['state'] == 'activated':
        central_policy_dict = vmanage_central_policy.get_central_policy_dict(remove_key=False)
        if vmanage.params['name'] in central_policy_dict:
            if not central_policy_dict[vmanage.params['name']]['isPolicyActivated']:
                vmanage.result['changed'] = True
                if not module.check_mode:
                    action_id = vmanage_central_policy.activate_central_policy(vmanage.params['name'],
                                                                               central_policy_dict[vmanage.params['name']]['policyId'])
                    if action_id:
                        if vmanage.params['wait']:
                            vmanage_utils.waitfor_action_completion(action_id)
                    else:
                        vmanage.fail_json(msg='Did not get action ID after attaching device to template.')

        else:
            # TODO: The reference to 'policy' in the following line is wrong. What should it be?
            vmanage.fail_json(msg="Cannot find central policy {0}".format(vmanage.params['name']))
    if vmanage.params['state'] in ['absent', 'deactivated']:
        central_policy_dict = vmanage_central_policy.get_central_policy_dict(remove_key=False)
        if policy['policyName'] in central_policy_dict:
            if central_policy_dict[policy['policyName']]['isPolicyActivated']:
                vmanage.result['changed'] = True
                if not module.check_mode:
                    action_id = vmanage_central_policy.deactivate_central_policy(vmanage.params['name'])
                    if action_id:
                        if vmanage.params['wait']:
                            vmanage_central_policy.waitfor_action_completion(action_id)
                    else:
                        vmanage.fail_json(msg='Did not get action ID after attaching device to template.')
        else:
            vmanage.fail_json(msg="Cannot find central policy {0}".format(policy['policyName']))

    vmanage.params['updates'] = central_policy_updates
    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
