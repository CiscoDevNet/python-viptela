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
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         aggregate=dict(type='list'),
                         name=dict(type='str'),
                         description = dict(type = 'str'),
                         type = dict(type ='str', required = False, choices= ['all', 'color', 'vpn', 'site', 'app',
                            'dataprefix', 'prefix', 'aspath', 'class', 'community', 'extcommunity', 'mirror', 'tloc',
                            'sla', 'policer', 'ipprefixall', 'dataprefixall'], default='all'),
                         entries = dict(type ='list'),
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
    viptela = viptelaModule(module)

    # Always as an aggregate... make a list if just given a single entry
    if viptela.params['aggregate']:
        policy_list =  viptela.params['aggregate']
    else:
        policy_list = [
            {
                "name": viptela.params['name'],
                "description": viptela.params['description'],
                "type": viptela.params['type'],
                "entries": viptela.params['entries'],
            }
        ]

    policy_list_dict = viptela.get_policy_list_dict(viptela.params['type'], remove_key=False)

    compare_values = ["name", "description", "type", "entries"]

    # Import site lists
    for list in policy_list:
        if viptela.params['state'] == 'present':
            if list['name'] in policy_list_dict:
                # FIXME Just compare the entries for now.
                if (list['entries'] != policy_list_dict[list['name']]['entries']) or viptela.params['force']:
                    list['listId'] = policy_list_dict[list['name']]['listId']
                    viptela.result['new_entries'] = list['entries']
                    viptela.result['existing_entries'] = policy_list_dict[list['name']]['entries']
                    # If description is not specified, try to get it from the existing information
                    if not list['description']:
                        list['description'] = policy_list_dict[list['name']]['description']
                    viptela.result['changed'] = True
                    if not module.check_mode:
                        viptela.result['put_payload'] = list
                        response = viptela.request('/dataservice/template/policy/list/{0}/{1}'.format(list['type'].lower(), list['listId']),
                                        method='PUT', payload=list)
                        viptela.result['response'] = response.json
                        if response.json:
                            # Updating the policy list returns a `processId` that locks the list and 'masterTemplatesAffected'
                            # that lists the templates affected by the change.
                            if 'processId' in response.json:
                                process_id = response.json['processId']
                                viptela.result['put_payload'] = response.json['processId']
                                if viptela.params['push']:
                                    # If told to push out the change, we need to reattach each template affected by the change
                                    for template_id in response.json['masterTemplatesAffected']:
                                        action_id = viptela.reattach_device_template(template_id, process_id=process_id)

                                # Delete the lock on the policy list
                                # FIXME: The list does not seem to update when we unlock too soon, so I think that we need
                                # to wait for the attachment, but need to understand this better.
                                # response = viptela.request('/dataservice/template/lock/{0}'.format(process_id), method='DELETE')
                                # viptela.result['lock_response'] = response.json
                            else:
                                if viptela.params['push']:
                                    viptela.fail_json(msg="Cannot push changes: Did not get a process id when updating policy list")
            else:
                if not module.check_mode:
                    viptela.request('/dataservice/template/policy/list/{0}/'.format(list['type'].lower()),
                                    method='POST', payload=list)
                viptela.result['changed'] = True
        else:
            if list['name'] in policy_list_dict:
                if not module.check_mode:
                    viptela.request('/dataservice/template/policy/list/{0}/{1}'.format(list['type'].lower(), list['listId']),
                                    method='DELETE')
                viptela.result['changed'] = True

    viptela.logout()
    viptela.exit_json(**viptela.result)

def main():
    run_module()

if __name__ == '__main__':
    main()

# https://192.133.178.76:8443/dataservice/template/lock/push_feature_template_configuration-2e133445-ae15-49ab-b74a-c1fe65e263b6