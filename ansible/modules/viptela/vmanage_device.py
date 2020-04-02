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
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         name=dict(type='str'),
                         transport_ip=dict(type='str', aliases=['device_ip', 'system_ip']),
                         uuid=dict(type='str', alias='deviceIP'),
                         personality=dict(type='str', choices=['vmanage', 'vsmart', 'vbond', 'vedge'], default='vedge'),
                         device_username=dict(type='str', alias='device_user'),
                         device_password=dict(type='str')
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

    if viptela.params['personality'] == 'vedge':
        device_type = 'vedges'
    else:
        device_type = 'controllers'

    device = {}
    if viptela.params['uuid']:
        device = viptela.get_device_status(viptela.params['uuid'], key='uuid')
    # See if we can find the device by deviceIP
    if not device and viptela.params['transport_ip']:
        device = viptela.get_device_status(viptela.params['transport_ip'])
    # If we could not find the device by deviceIP, see if we can find it be (host)name
    if not device and viptela.params['name']:
        device = viptela.get_device_status(viptela.params['name'], key='host-name')

    viptela.result['device'] = device
    if viptela.params['state'] == 'present':
        if device:
            # Can't really change anything
            pass
        else:
            viptela.result['what_changed'].append('new')
            if not viptela.params['device_username'] or not viptela.params['device_password']:
                viptela.fail_json(msg="device_username and device_password must be specified when add a new device")
            if not module.check_mode:
                response = viptela.create_controller(viptela.params['transport_ip'], viptela.params['personality'],
                                                     viptela.params['device_username'], viptela.params['device_password'])
                viptela.result['response'] = response
    else:
        if device and device_type == 'controllers':
            if not module.check_mode:
                viptela.delete_controller(device['uuid'])
        elif device and device_type == 'vedges':
            device_config = viptela.get_device_by_uuid(device['uuid'], type=device_type)
            if 'vedgeCertificateState' in device_config and device_config['vedgeCertificateState'] != 'tokengenerated':
                viptela.result['what_changed'].append('delete')
                if not module.check_mode:
                    viptela.decommision_device(device['uuid'])

    if viptela.result['what_changed']:
        viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
