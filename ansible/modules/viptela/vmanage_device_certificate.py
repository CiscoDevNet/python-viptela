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
    argument_spec.update(state=dict(type='str', choices=['csr', 'cert', 'push'], default='cert'),
                         name=dict(type='str'),
                         transport_ip=dict(type='str', aliases=['device_ip', 'system_ip']),
                         cert=dict(type='str', alias='deviceEnterpriseCertificate'),
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

    device = {}
    # See if we can find the device by deviceIP
    if viptela.params['transport_ip']:
        device = viptela.get_device_by_device_ip(viptela.params['transport_ip'], type='controllers')
    # If we could not find the device by deviceIP, see if we can find it be (host)name
    if not device:
        device = viptela.get_device_by_name(viptela.params['name'], type='controllers')

    if viptela.params['state'] == 'cert':
        if device:
            if not viptela.params['cert']:
                viptela.fail_json(msg="'cert' is required when added a certificate to a device")
            if device:
                if ('deviceEnterpriseCertificate' not in device) or (viptela.params['cert'] != device['deviceEnterpriseCertificate']):
                    viptela.result['what_changed'].append('deviceEnterpriseCertificate')
                    if not module.check_mode:
                        viptela.install_device_cert(viptela.params['cert'])
            else:
                viptela.fail_json(msg="Device must exist to add it's certificate")
        else:
            viptela.fail_json(msg="Device not found")
    elif viptela.params['state'] == 'csr':
        if 'deviceCSR' in device:
            viptela.result['deviceCSR'] = device['deviceCSR']
        else:
            viptela.result['what_changed'].append('csr')
            if not module.check_mode:
                if 'deviceIP' in device:
                    viptela.result['deviceCSR'] = viptela.generate_csr(device['deviceIP'])
                else:
                    viptela.fail_json(msg="Cannot find deviceIP for {0}".format(viptela.params['name']))
    elif viptela.params['state'] == 'push':
        viptela.push_certificates()

    if viptela.result['what_changed']:
        viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
