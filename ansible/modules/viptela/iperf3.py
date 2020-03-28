#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: iperf3_package

short_description: This is my sample module

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    name:
        description:
            - The name of the package
        required: true
    state:
        description:
            - The state if the bridge ('present' or 'absent') (Default: 'present')
        required: false
    file:
        description:
            - The file name of the package
        required: false

author:
    - Steven Carter
'''

EXAMPLES = '''
# Upload and register a package
- name: Package
  iperf3_package:
    host: 1.2.3.4
    user: admin
    password: cisco
    file: asav.tar.gz
    name: asav
    state: present

# Deregister a package
- name: Package
  iperf3_package:
    host: 1.2.3.4
    user: admin
    password: cisco
    name: asav
    state: absent
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

# import requests
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.iperf3 import iperf3Module, iperf3_argument_spec
import iperf3

def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec= (host=dict(type='str', required=True),
                    duration=dict(type='int', defailt 1),
                    bind_address=dict(type='str'),
                    port=dict(type='int', default=5001),
                    blksize=dict(type='int'),
                    streams=dict(type='int', default=1),
                    zerocopy=dict(type=True),
                    verbose=dict(type='bool'),
                    reverse=dict(type='bool', default=True),
                    protocol=dict(type='str', choices=['tcp', 'udp'], default='tcp')
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

    client = iperf3.Client()
    client.server_hostname = module.params['host']
    if module.params['duration']:
        client.duration = module.params['duration']

    if module.params['port']:
        client.port = module.params['port']

    if module.params['protocol']:
        client.protocol = module.params['protocol']

    if module.params['bind_address']:
        client.bind_address = module.params['bind_address']

    if module.params['blksize']:
        client.blksize = module.params['blksize']

    if module.params['streams']:
        client.num_streams = module.params['streams']

    if  module.params['zerocopy']:
        client.zerocopy = module.params['zerocopy']

    if module.params['reverse']:
        client.reverse = module.params['reverse']

    result['stats'] = client.run()

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result


    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # FIXME: Work with iperf3 so they can implement a check mode
    if module.check_mode:
        module.exit_json(**iperf3.result)

    # execute checks for argument completeness

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**iperf3.result)

def main():
    run_module()

if __name__ == '__main__':
    main()