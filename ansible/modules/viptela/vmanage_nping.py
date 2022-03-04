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
    argument_spec.update(vedge=dict(type='str', required=True),
                         dst_ip=dict(type='str', required=True, alias='host'),
                         vpn=dict(type='int', default=0, required=False),
                         src_interface=dict(type='str', required=False, alias='source'),
                         probe_type=dict(type='str', required=False, default='icmp', alias='probeType'),
                         count=dict(type='str', required=False),
                         size=dict(type='str', required=False),
                         df=dict(type='str', required=False),
                         rapid=dict(type='bool', required=False),
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
    device = {}
    device = viptela.get_device_by_name(viptela.params['vedge'])

    if device:
        system_ip = device['system-ip']
    else:
        viptela.fail_json(msg="Cannot find vedge {0}".format(viptela.params['vedge']))

    payload = {
        'host': viptela.params['dst_ip'],
        'vpn': str(viptela.params['vpn']),
        'probeType': viptela.params['probe_type'],
    }
    if viptela.params['src_interface']:
        payload['source'] = viptela.params['src_interface']
    if viptela.params['count']:
        payload['count'] = viptela.params['count']
    if viptela.params['size']:
        payload['size'] = viptela.params['size']
    if viptela.params['df']:
        payload['df'] = viptela.params['df']
    if viptela.params['rapid']:
        payload['rapid'] = "true" if viptela.params['rapid'] else "false"

    response = viptela.request('/dataservice/device/tools/nping/{0}'.format(system_ip), method='POST', payload=payload)
    if response.json:
        viptela.result['json'] = response.json

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()

# https://192.133.178.190:8443/dataservice/device/tools/nping/10.255.210.1
# {"host": "10.23.3.10", "vpn": "0", "source": "ge0/0", "probeType": "icmp"}
# {"host":"10.22.3.10","vpn":"10","count":"5","size":"1500","probeType":"icmp","df":"true"}
