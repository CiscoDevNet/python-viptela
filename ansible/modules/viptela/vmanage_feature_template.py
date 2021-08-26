#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.viptela.vmanage import Vmanage, vmanage_argument_spec
from vmanage.api.feature_templates import FeatureTemplates
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
                         definition=dict(type='dict', alias='templateDefinition'),
                         template_type=dict(type='str', alias='templateType'),
                         device_type=dict(type='list', alias='deviceType'),
                         template_min_version=dict(type='str', alias='templateMinVersion'),
                         factory_default=dict(type='bool', alias='factoryDefault'),
                         url=dict(type='bool', alias='templateUrl'),
                         update=dict(type='bool', default=True),
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
    vmanage_feature_templates = FeatureTemplates(vmanage.auth, vmanage.host)
    vmanage_template_data = TemplateData(vmanage.auth, vmanage.host)

    # Always as an aggregate... make a list if just given a single entry
    if vmanage.params['aggregate']:
        feature_template_list = vmanage.params['aggregate']
    else:
        if vmanage.params['state'] == 'present':
            try:

                feature_template_list = [
                    {
                        'templateName': vmanage.params['name'],
                        'templateDescription': vmanage.params['description'],
                        'deviceType': vmanage.params['device_type'],
                        'templateDefinition': vmanage.params['definition'],
                        'templateType': vmanage.params['template_type'],
                        'templateMinVersion': vmanage.params['template_min_version'],
                        'factoryDefault': vmanage.params['factory_default']
                    }
                ]
            except:
                module.fail_json(
                    msg="Required values: name, description, device_type, definition, template_type, template_min_version, factory_default")
        else:
            try:
                feature_template_list = [
                    {
                        'templateName': vmanage.params['name']
                    }
                ]
            except:
                module.fail_json(
                    msg='Required values: name'
                )

    feature_template_updates = []
    if vmanage.params['state'] == 'present':
        feature_template_updates = vmanage_template_data.import_feature_template_list(
            feature_template_list,
            check_mode=module.check_mode,
            update=vmanage.params['update'],
            push=vmanage.params['push']
        )
        if feature_template_updates:
            vmanage.result['changed'] = True

    else:
        feature_template_dict = vmanage_feature_templates.get_feature_template_dict(factory_default=True, remove_key=False)
        for feature_template in feature_template_list:
            if feature_template['templateName'] in feature_template_dict:
                if not module.check_mode:
                    vmanage_feature_templates.delete_feature_template(feature_template_dict[feature_template['templateName']]['templateId'])
                vmanage.result['changed'] = True

    vmanage.result['updates'] = feature_template_updates
    vmanage.exit_json(**vmanage.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
