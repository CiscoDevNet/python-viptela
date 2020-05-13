#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.data.template_data import TemplateData


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(factory_default=dict(type='bool', default=False),
                         )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )
    vmanage = Vmanage(module)
    template_data = TemplateData(vmanage.auth, vmanage.host)

    vmanage.result['device_templates'] = template_data.export_device_template_list(factory_default=vmanage.params['factory_default'])

    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
