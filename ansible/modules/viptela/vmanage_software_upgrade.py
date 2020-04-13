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
    argument_spec.update(devices=dict(type='list'),
                         deviceType=dict(type='str', choices=['controller', 'vedge'], default='vedge'),
                         version=dict(type='str'),
                         activate=dict(type='bool'),
                         set_default=dict(type='bool')
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

    # It seems to me that the software operations on the vManage are already idempotent
    # This is why at least in this phase we are not implementing other idempotency checks
    # In future it might make sense to implement them to avoid generating useless tasks
    # on the vManage. This would streamline operations.
    # TODO Add idempotency cheks to this module

    devices = module.params['devices']
    deviceType = module.params['deviceType']
    version = module.params['version']
    data = [
        {
            "family": "vedge-x86",
            "version": version
        }
    ]
    reboot = module.params['activate']
    set_default = module.params['set_default']

    # Verify if the target software (version) is available in the vManage and set flag
    vManage_software_list = viptela.get_software_images_list()
    software_present_on_vManage = False
    for software in vManage_software_list:
        if version == software['versionName']:
            software_present_on_vManage = True

    # If we have found the software we can move on and perform the operation
    if software_present_on_vManage:
        viptela.software_install(devices, deviceType, data, reboot)

        if set_default:
            for device in devices:
                device.update({'version': version})
            viptela.set_default_partition(devices, deviceType)

    # If not, we fail
    else:
        module.fail_json(
            msg="We don't have this software, I am sorry")

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
