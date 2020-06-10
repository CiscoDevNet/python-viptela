#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import requests
import os.path
# from requests.auth import HTTPBasicAuth
# from paramiko import SSHClient
# from scp import SCPClient
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela.viptela import viptelaModule, viptela_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(file=dict(type='str', required=True),
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
    viptela = viptelaModule(module)

    filename = os.path.basename(module.params['file'])

    payload = {
        'Content-Type': 'application/x-tar',
        'Content-Disposition': 'form-data; name="file"; filename=' + filename
        }

    if not module.check_mode:
        response = viptela.request('/dataservice/device/action/software/package/virtualmachine', method='POST',
                                   files={'file': open(module.params['file'], 'rb')},
                                   data={'validity': 'valid', 'upload': 'true'},
                                   headers=None)

        if response.status_code == 200:
            viptela.exit_json(changed=True)
        else:
            viptela.fail_json(msg="Upload failed")

def main():
    run_module()


if __name__ == '__main__':
    main()
