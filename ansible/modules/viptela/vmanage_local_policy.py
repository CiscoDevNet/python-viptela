#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.local_policy import LocalPolicy
from vmanage.data.policy_data import PolicyData

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

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

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )
    vmanage = Vmanage(module)
    vmanage_local_policy = LocalPolicy(vmanage.auth, vmanage.host)
    policy_data = PolicyData(vmanage.auth, vmanage.host)

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

    local_policy_updates = []
    if vmanage.params['state'] == 'present':
        local_policy_updates = policy_data.import_local_policy_list(
            policy_list,
            check_mode=module.check_mode,
            update=vmanage.params['update'],
            push=vmanage.params['push']
        )
        if local_policy_updates:
            vmanage.result['changed'] = True
    elif vmanage.params['state'] == 'absent':
        local_policy_dict = vmanage_local_policy.get_local_policy_dict(remove_key=False)
        for policy in policy_list:
            if policy in local_policy_dict:
                if not module.check_mode:
                    vmanage_local_policy.delete_local_policy(local_policy_dict[policy['policyName']]['policyId'])
                vmanage.result['changed'] = True

    vmanage.params['updates'] = local_policy_updates
    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
