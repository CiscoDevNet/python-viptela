#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela.viptela import viptelaModule, viptela_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(name=dict(type='str'),
                         device_ip=dict(type='str', alias='deviceIP'),
                         uuid=dict(type='str'),
                         model=dict(type='str'),
                         version=dict(type='str', default='v1'),
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
    viptela.result['bootstrap'] = {}
    device = {}
    uuid = None
    if viptela.params['uuid']:
        uuid = viptela.params['uuid']
        device = viptela.get_device_by_uuid(viptela.params['uuid'])
    elif viptela.params['device_ip']:
        # See if we can find the device by deviceIP
        device = viptela.get_device_by_device_ip(viptela.params['device_ip'])
        if 'uuid' in device:
            uuid = device['uuid']
    elif viptela.params['name']:
        device = viptela.get_device_by_name(viptela.params['name'])
        if 'uuid' in device:
            uuid = device['uuid']

    if uuid:
        if device['vedgeCertificateState'] in ['tokengenerated', 'bootstrapconfiggenerated']:
            # We can only generate bootstrap in these two states.  Otherwise, the
            # device is in-use and cannot be bootstrapped.
            viptela.result['what_changed'].append('bootstrap')
            if not module.check_mode:
                bootstrap = viptela.generate_bootstrap(uuid, viptela.params['version'])
                viptela.result['uuid'] = uuid
                viptela.result['bootstrap'] = bootstrap
    elif viptela.params['model']:
        # if no uuid was specified, just grab the first free device
        device = viptela.get_unused_device(viptela.params['model'])
        if not device:
            viptela.fail_json(msg="Could not find available device")
        viptela.result['what_changed'].append('bootstrap')
        if not module.check_mode:
            bootstrap = viptela.generate_bootstrap(device['uuid'], viptela.params['version'])
            viptela.result['bootstrap'] = bootstrap
    else:
        viptela.fail_json(msg="Could not find UUID with supplied arguments")

    if viptela.result['what_changed']:
        viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
