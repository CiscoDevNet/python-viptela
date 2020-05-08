#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.policy_lists import PolicyLists
from vmanage.data.policy_data import PolicyData


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         aggregate=dict(type='list'),
                         name=dict(type='str'),
                         description=dict(type='str'),
                         type=dict(type='str', required=False, choices=['all', 'color', 'vpn', 'site', 'app',
                                                                        'dataprefix', 'prefix', 'aspath', 'class', 'community',
                                                                        'extcommunity', 'mirror', 'tloc',
                                                                        'sla', 'policer', 'ipprefixall', 'dataprefixall'], default='all'),
                         entries=dict(type='list'),
                         update=dict(type='bool', default=False),
                         push=dict(type='bool', default=False),
                         force=dict(type='bool', default=False)
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
    vmanage_policy_lists = PolicyLists(vmanage.auth, vmanage.host)
    vmanage_policy_data = PolicyData(vmanage.auth, vmanage.host)

    # Always as an aggregate... make a list if just given a single entry
    if vmanage.params['aggregate']:
        policy_list_list = vmanage.params['aggregate']
    else:
        policy_list_list = [
            {
                "name": vmanage.params['name'],
                "description": vmanage.params['description'],
                "type": vmanage.params['type'],
                "entries": vmanage.params['entries'],
            }
        ]

    # Import site lists
    policy_list_updates = []
    if vmanage.params['state'] == 'present':
        policy_list_updates = vmanage_policy_data.import_policy_list_list(
            policy_list_list,
            check_mode=module.check_mode,
            update=vmanage.params['update'],
            push=vmanage.params['push']
        )
        if policy_list_updates:
            vmanage.result['changed'] = True
    else:
        policy_list_dict = vmanage_policy_lists.get_policy_list_dict(vmanage.params['type'], remove_key=False)
        for policy_list in policy_list_list:
            if policy_list['name'] in policy_list_dict:
                diff = list(dictdiffer.diff({}, policy_list))
                policy_list_updates.append({'name': policy_list['name'], 'diff': diff})
                if not module.check_mode:
                    vmanage_policy_lists.delete_policy_list(policy_list['type'].lower(), policy_list['listId'])
                vmanage.result['changed'] = True

    vmanage.params['updates'] = policy_list_updates
    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
