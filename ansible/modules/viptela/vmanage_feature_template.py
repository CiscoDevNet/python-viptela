#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela import viptelaModule, viptela_argument_spec
from collections import OrderedDict

def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         name=dict(type='str', alias='templateName'),
                         description=dict(type='str', alias='templateDescription'),
                         definition=dict(type='dict', alias='templateDefinition'),
                         template_type=dict(type='str', alias='templateType'),
                         device_type=dict(type='list', alias='deviceType'),
                         template_min_version=dict(type='str', alias='templateMinVersion'),
                         factory_default=dict(type='bool', alias='factoryDefault'),
                         url=dict(type='bool', alias='templateUrl'),
                         aggregate=dict(type='list'),
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

    # Always as an aggregate... make a list if just given a single entry
    if viptela.params['aggregate']:
        feature_template_list = viptela.params['aggregate']
    else:
        if viptela.params['state'] == 'present':
            try:

                feature_template_list = [
                    {
                        'templateName': viptela.params['name'],
                        'templateDescription': viptela.params['description'],
                        'deviceType': viptela.params['device_type'],
                        'templateDefinition': viptela.params['definition'],
                        'templateType': viptela.params['template_type'],
                        'templateMinVersion': viptela.params['template_min_version'],
                        'factoryDefault': viptela.params['factory_default']
                    }
                ]
            except:
                module.fail_json(
                    msg="Required values: name, description, device_type, definition, template_type, template_min_version, factory_default")
        else:
            try:
                feature_template_list = [
                    {
                        'templateName': viptela.params['name']
                    }
                ]
            except:
                module.fail_json(
                    msg='Required values: name'
                )

    feature_template_dict = viptela.get_feature_template_dict(factory_default=True, remove_key=False)

    ignore_values = ["lastUpdatedOn", "lastUpdatedBy", "templateId", "createdOn", "createdBy"]
    compare_values = ['templateDescription', 'deviceType', 'templateType', 'templateDefinition', 'templateMinVersion']

    for feature_template in feature_template_list:
        if viptela.params['state'] == 'present':
            payload = {
                'templateName': feature_template['templateName'],
                'templateDescription': feature_template['templateDescription'],
                'deviceType': feature_template['deviceType'],
                'templateType': feature_template['templateType'],
                'templateMinVersion': feature_template['templateMinVersion'],
                'factoryDefault': feature_template['factoryDefault'],
                'templateDefinition': feature_template['templateDefinition']
            }
            # FIXME (Issue #1): This is a temporary workaround for the fact that vManage requires it payload in a specific order
            template_definition = OrderedDict()
            if 'if-name' in feature_template['templateDefinition']:
                template_definition['if-name'] = feature_template['templateDefinition'].pop('if-name')
            if 'vpn-id' in feature_template['templateDefinition']:
                template_definition['vpn-id'] = feature_template['templateDefinition'].pop('vpn-id')
            for key, value in feature_template['templateDefinition'].items():
                template_definition[key] = value
            payload['templateDefinition'] = template_definition
            if payload['templateName'] in feature_template_dict:
                viptela.result['changed'] = False
                # changed_items = viptela.compare_payloads(payload, feature_template_dict[payload['templateName']], compare_values=compare_values)
                # if changed_items:
                #     viptela.result['changed'] = True
                #     viptela.result['what_changed'] = changed_items
                #     if not module.check_mode:
                #         viptela.request('/dataservice/template/feature/{0}'.format(feature_template_dict[payload['templateName']]['templateId']),
                #                         method='PUT', payload=payload)
            else:
                if not module.check_mode:
                    viptela.request('/dataservice/template/feature/', method='POST', payload=payload)
                viptela.result['changed'] = True
        else:
            if feature_template['templateName'] in feature_template_dict:
                if not module.check_mode:
                    viptela.request('/dataservice/template/feature/{0}'.format(
                        feature_template_dict[feature_template['templateName']]['templateId']),
                                    method='DELETE')
                viptela.result['changed'] = True

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
