#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.device import Device
from vmanage.api.monitor_network import MonitorNetwork
import ipaddress


subset_options = ['config', 'omp', 'control']

def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = vmanage_argument_spec()
    argument_spec.update(device=dict(type='str', aliases=['device', 'host-name']),
                         gather_subset=dict(type='list', options=subset_options),
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
    vmanage_device = Device(vmanage.auth, vmanage.host)
    vmanage_monitor = MonitorNetwork(vmanage.auth, vmanage.host)

    
    if vmanage.params['device']:
        # If we are passed in a device, we return specific facts about that device

        device_facts = {}
        # Check to see if we were passed in a device IP address or a device name
        try:
            system_ip = ipaddress.ip_address(vmanage.params['device'])
            device_status = vmanage_device.get_device_status(system_ip)
        except ValueError:
            device_status = vmanage_device.get_device_status(vmanage.params['device'], key='host-name')
            system_ip = device_status['system-ip']

        if device_status:
            if vmanage.params['gather_subset']:
                requested_subsets = vmanage.params['gather_subset']
            else:
                requested_subsets = subset_options
            device_facts['status'] = device_status
            if 'config' in requested_subsets:
                device_facts['config'] = vmanage_device.get_device_config(device_status['device-type'], system_ip)
            if 'omp' in requested_subsets:
                omp_routes_received = vmanage_monitor.get_omp_routes_received(system_ip)
                omp_routes_advertised = vmanage_monitor.get_omp_routes_advertised(system_ip)
                omp_routes = {
                        'received': omp_routes_received,
                        'advertised': omp_routes_advertised,
                    }
                omp = {
                    'routes': omp_routes
                }
                device_facts['omp'] = omp
            if 'control' in requested_subsets:
                control_connections = vmanage_monitor.get_control_connections(system_ip)
                control_connections_history = vmanage_monitor.get_control_connections_history(system_ip)
                control = {
                    'connections': control_connections,
                    'connections_history': control_connections_history
                }
                device_facts['control'] = control
        vmanage.result['device_facts'] = device_facts
    else:
        if vmanage.params['gather_subset']:
            vmanage.fail_json(msg="gather_subset argument can only be secified with device argument", **vmanage.result)
        # Otherwise, we return facts for all devices sorted by device type
        vmanage.result['vedges'] = vmanage_device.get_device_config_list('vedges')
        vmanage.result['controllers'] = vmanage_device.get_device_config_list('controllers')

    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
