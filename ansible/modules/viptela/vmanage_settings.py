#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela.viptela import viptelaModule, viptela_argument_spec
from collections import OrderedDict


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(organization=dict(type='str'),
                         vbond=dict(type='str'),
                         vbond_port=dict(type='str', default='12346'),
                         root_cert=dict(type='str'),
                         ca_type=dict(type='str')
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
    viptela.result['what_changed'] = []

    if viptela.params['organization']:
        current = viptela.get_vmanage_org()
        if viptela.params['organization'] != current:
            viptela.result['what_changed'].append('organization')
            if not module.check_mode:
                viptela.set_vmanage_org(viptela.params['organization'])

    if viptela.params['vbond']:
        current = viptela.get_vmanage_vbond()
        if viptela.params['vbond'] != current['vbond'] or viptela.params['vbond_port'] != current['vbond_port']:
            viptela.result['what_changed'].append('vbond')
            if not module.check_mode:
                viptela.set_vmanage_vbond(viptela.params['vbond'], viptela.params['vbond_port'])

    if viptela.params['ca_type']:
        current = viptela.get_vmanage_ca_type()
        if viptela.params['ca_type'] != current:
            viptela.result['what_changed'].append('ca_type')
            if not module.check_mode:
                viptela.set_vmanage_ca_type(viptela.params['ca_type'])

    if viptela.params['root_cert']:
        current = viptela.get_vmanage_root_cert()
        if viptela.params['root_cert'] not in current:
            viptela.result['what_changed'].append('root_cert')
            if not module.check_mode:
                viptela.set_vmanage_root_cert(viptela.params['root_cert'])

    if viptela.result['what_changed']:
        viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
