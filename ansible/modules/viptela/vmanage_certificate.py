#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.certificate import Certificate

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(organization=dict(type='str'),
                         vbond=dict(type='str'),
                         vbond_port=dict(type='int', default=12346),
                         root_cert=dict(type='str'),
                         push=dict(type='bool')
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
    vmanage_certificate = Certificate(vmanage.auth, vmanage.host)

    vmanage.result['what_changed'] = []

    if vmanage.params['push']:
        vmanage_certificate.push_certificates()

    if vmanage.result['what_changed']:
        vmanage.result['changed'] = True

    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
