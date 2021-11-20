#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import time
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela.viptela import viptelaModule, viptela_argument_spec


def run_module():
    action_id = None
    action_status = None
    action_activity = None
    action_config = None

    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present', 'query'], default='present'),
                         device_name=dict(type='str', aliases=['device', 'host-name']),
                         device_ip=dict(type='str', aliases=['system_ip']),
                         site_id=dict(type='str'),
                         uuid=dict(type='str'),
                         personality=dict(type='str', choices=['vmanage', 'vsmart', 'vbond', 'vedge'], default='vedge'),
                         template=dict(type='str'),
                         variables=dict(type='dict', default={}),
                         wait=dict(type='bool', default=False),
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

    if viptela.params['personality'] == 'vedge':
        device_type = 'vedges'
    else:
        device_type = 'controllers'

    if viptela.params['uuid']:
        device_data = viptela.get_device_by_uuid(viptela.params['uuid'], type=device_type)
        if 'uuid' not in device_data:
            viptela.fail_json(msg='Cannot find device with UUID: {0}.'.format(viptela.params['uuid']))
        # If this is a preallocation, we need to set these things.
        if 'system-ip' not in device_data or len(device_data['system-ip']) == 0:
            if viptela.params['system_ip']:
                device_data['system-ip'] = viptela.params['system_ip']
            else:
                viptela.fail_json(msg='system_ip is needed when pre-attaching templates')
        if 'deviceIP' not in device_data or len(device_data['deviceIP']) == 0:
            if viptela.params['system_ip']:
                device_data['deviceIP'] = viptela.params['system_ip']
            else:
                viptela.fail_json(msg='system_ip is needed when pre-attaching templates')
        if 'site-id' not in device_data or len(device_data['site-id']) == 0:
            if viptela.params['site_id']:
                device_data['site-id'] = viptela.params['site_id']
            else:
                viptela.fail_json(msg='site_id is needed when pre-attaching templates')
        if 'host-name' not in device_data or len(device_data['host-name']) == 0:
            if viptela.params['device_name']:
                device_data['host-name'] = viptela.params['device_name']
            else:
                viptela.fail_json(msg='device_name is needed when pre-attaching templates')
    elif viptela.params['device_name']:
        device_status = viptela.get_device_status(viptela.params['device_name'], key='host-name')
        if 'uuid' in device_status:
            device_type = 'controllers' if device_status['personality'] in ['vmanage', 'vbond', 'vsmart'] else 'vedges'
            device_data = viptela.get_device_by_uuid(device_status['uuid'], type=device_type)
        else:
            viptela.fail_json(msg='Cannot find device with name: {0}.'.format(viptela.params['device']))

    if viptela.params['state'] == 'present':
        if 'system-ip' not in device_data:
            viptela.fail_json(msg='system-ip must be defined for {0}.'.format(viptela.params['device']))
        if 'site-id' not in device_data:
            viptela.fail_json(msg='site-id must be defined for {0}.'.format(viptela.params['device']))

        # Get template data and see if it is a real template
        device_template_dict = viptela.get_device_template_dict(factory_default=True)
        if viptela.params['template']:
            if viptela.params['template'] not in device_template_dict:
                viptela.fail_json(msg='Template {0} not found.'.format(viptela.params['template']))
            template_data = device_template_dict[viptela.params['template']]
        else:
            viptela.fail_json(msg='Must specify a template with state present')

        # Make sure they passed in the required variables
        # get_template_variables provides a variable name -> property mapping
        template_variables = viptela.get_template_variables(device_template_dict[viptela.params['template']]['templateId'])
        optional_template_variables = viptela.get_template_optional_variables(
            device_template_dict[viptela.params['template']]['templateId'])
        mandatory_template_variables = {k: template_variables[k] for k in set(template_variables) - set(optional_template_variables)}
        if mandatory_template_variables:
            if viptela.params['variables']:
                for variable in mandatory_template_variables:
                    if variable not in viptela.params['variables']:
                        viptela.fail_json(
                            msg='Template {0} requires variables: {1}'.format(viptela.params['template'], ', '.join(template_variables)))

        viptela.result['template_variables'] = template_variables

        # Construct the variable payload
        device_template_variables = {
            "csv-status": "complete",
            "csv-deviceId": device_data['uuid'],
            "csv-deviceIP": device_data['deviceIP'],
            "csv-host-name": device_data['host-name'],
            '//system/host-name': device_data['host-name'],
            '//system/system-ip': device_data['system-ip'],
            '//system/site-id': device_data['site-id'],
        }

        # For each of the variables passed in, match them up with the names of the variables requires in the
        # templates and add them with the corresponding property.  The the variables is not in template_variables,
        # just leave it out since it is not required.
        for key, value in viptela.params['variables'].items():
            if key in template_variables:
                property_value = template_variables[key]
                device_template_variables[property_value] = viptela.params['variables'][key]

        # When dealing with optional parameters if we do not have explicitely set a value for it
        # we must add the optional parameter to the payload with { key: 'TEMPLATE_IGNORE'}
        for key, value in optional_template_variables.items():
            property_value = template_variables[key]
            if property_value not in device_template_variables:
                device_template_variables[property_value] = 'TEMPLATE_IGNORE'

        attached_uuid_list = viptela.get_template_attachments(template_data['templateId'], key='uuid')

        if device_data['uuid'] in attached_uuid_list:
            # Add the template ID to the device's variable payload because we'll need it for comparison and update.
            # device_template_variables['csv-templateId'] = template_data['templateId']
            # The device is already attached to the template.  We need to see if any of the input changed, so we make
            # an API call to get the input on last attach
            payload = {
                "templateId": template_data['templateId'],
                "deviceIds": [device_data['uuid']],
                "isEdited": "true",
                "isMasterEdited": "false"
            }
            response = viptela.request('/dataservice/template/device/config/input/', method='POST', payload=payload)
            if response.json and 'data' in response.json:
                current_variables = response.json['data'][0]
                # viptela.result['old'] = current_variables
                # viptela.result['new'] = device_template_variables
                # Convert both to a string and compare.  For some reason, there can be an int/str
                # mismatch.  It might be indicative of a problem...
                for property in device_template_variables:
                    if str(device_template_variables[property]) != str(current_variables[property]):
                        viptela.result['changed'] = True
        else:
            viptela.result['changed'] = True

        if not module.check_mode and viptela.result['changed']:
            payload = {
                "deviceTemplateList":
                    [
                        {
                            "templateId": template_data['templateId'],
                            "device": [device_template_variables],
                            "isEdited": False,
                            "isMasterEdited": False
                        }
                    ]
            }
            response = viptela.request('/dataservice/template/device/config/attachfeature', method='POST', payload=payload)
            if response.json:
                action_id = response.json['id']
            else:
                viptela.fail_json(msg='Did not get action ID after attaching device to template.')
    elif viptela.params['state'] == 'absent':
        if 'templateId' in device_data:
            viptela.result['changed'] = True
            payload = {
                "deviceType": device_data['deviceType'],
                "devices": [
                    {
                        "deviceId": device_data['uuid'],
                        "deviceIP": device_data['deviceIP']
                    }
                ]
            }
            if not module.check_mode:
                response = viptela.request('/dataservice/template/config/device/mode/cli', method='POST', payload=payload)
                if response.json:
                    action_id = response.json['id']
                else:
                    viptela.fail_json(msg='Did not get action ID after attaching device to template.')

    elif viptela.params['state'] == 'query':
        # Get template data and see if it is a real template
        device_template_dict = viptela.get_device_template_dict(factory_default=True)
        if viptela.params['template']:
            if viptela.params['template'] not in device_template_dict:
                viptela.fail_json(msg='Template {0} not found.'.format(viptela.params['template']))
            template_data = device_template_dict[viptela.params['template']]
        else:
            viptela.fail_json(msg='Must specify a template with state query')

        # get_template_variables provides a variable name -> property mapping
        template_variables = viptela.get_template_variables(device_template_dict[viptela.params['template']]['templateId'])
        optional_template_variables = viptela.get_template_optional_variables(
            device_template_dict[viptela.params['template']]['templateId'])
        viptela.result['template_variables'] = template_variables
        viptela.result['optional_template_variables'] = optional_template_variables
        viptela.result['mandatory_template_variables'] = {k: template_variables[k] for k in
                                                          set(template_variables) - set(optional_template_variables)}
    # If told, wait for the status of the request and report it
    if viptela.params['wait'] and action_id:
        viptela.waitfor_action_completion(action_id)

    viptela.logout()
    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
