#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.apps.files import Files


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(file=dict(type='str', required=True),
                         update=dict(type='bool', required=False, default=False),
                         push=dict(type='bool', required=False, default=False),
                         type=dict(type='str', required=False, choices=['feature', 'device'], default=None),
                         name_list=dict(type='list', required=False, default=[]),
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
    vmanage_files = Files(vmanage.auth, vmanage.host)
    vmanage.result['imported'] = vmanage_files.import_policy_from_file(vmanage.params['file'], update=vmanage.params['update'],
                                                                       check_mode=module.check_mode, push=vmanage.params['push'])

    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
