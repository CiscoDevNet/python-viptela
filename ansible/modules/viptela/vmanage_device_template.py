#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.device_templates import DeviceTemplates
from vmanage.data.template_data import TemplateData

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         name=dict(type='str', alias='templateName'),
                         description=dict(type='str', alias='templateDescription'),
                         templates=dict(type='str', alias='generalTemplates'),
                         device_type=dict(type='list', alias='deviceType'),
                         config_type=dict(type='list', alias='configType'),
                         update=dict(type='bool', defaut=True),
                         factory_default=dict(type='bool', alias='factoryDefault'),
                         aggregate=dict(type='list'),
                         push=dict(type='bool', default=False)
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
    vmanage_device_templates = DeviceTemplates(vmanage.auth, vmanage.host)
    vmanage_template_data = TemplateData(vmanage.auth, vmanage.host)

    # Always as an aggregate... make a list if just given a single entry
    if vmanage.params['aggregate']:
        device_template_list = vmanage.params['aggregate']
    else:
        if vmanage.params['state'] == 'present':
            device_template_list = [
                {
                    'templateName': vmanage.params['name'],
                    'templateDescription': vmanage.params['description'],
                    'deviceType': vmanage.params['device_type'],
                    'configType': vmanage.params['config_type'],
                    'factoryDefault': vmanage.params['factory_default'],
                    'generalTemplates': vmanage.params['templates'],
                }
            ]
        else:
            device_template_list = [
                {
                    'templateName': vmanage.params['name'],
                    'state': 'absent'
                }
            ]

    device_template_updates = []
    if vmanage.params['state'] == 'present':
        device_template_updates = vmanage_template_data.import_device_template_list(
            device_template_list,
            check_mode=module.check_mode,
            update=vmanage.params['update'],
            push=vmanage.params['push']
        )
        if device_template_updates:
            vmanage.result['changed'] = True
    else:
        device_template_dict = vmanage_device_templates.get_device_template_dict(
            factory_default=True, remove_key=False)
        for device_template in device_template_list:
            if device_template['templateName'] in device_template_dict:
                if not module.check_mode:
                    vmanage_device_templates.delete_device_template(device_template_dict[device_template['templateName']]['templateId'])
                vmanage.result['changed'] = True

    vmanage.result['updates'] = device_template_updates
    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
