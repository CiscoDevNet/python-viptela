#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}
#### CAN WE DO THIS ????
import os
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela.viptela import viptelaModule, viptela_argument_spec
from collections import OrderedDict


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         file=dict(type='str'),
                         aggregate=dict(type='list')
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

    if viptela.params['aggregate']:
        upload_software_list = viptela.params['aggregate']
    else:
        upload_software_list = [
            {
                'file': module.params['file']
            }
        ]

    # THIS MODULE IS DESIGNED TO UPLOAD UPGRADE IMAGES TO THE VMANAGE
    # Software in SD-WAN varies depending on what you want to upgrade.
    # This is a complication for what concern idempotency of this module
    # Files to upgrade vmanage will look like: vmanage-XX.YY.ZZ-<platform>.tar.gz
    # Files to upgrade vedge cloud/vedge 5k/vbond/vsmart will look like: viptela-XX.YY.ZZ-<platform>.tar.gz
    # Physical appliances will NOT have incremental upgrade images
    # CISCO Physical appliances will be upgraded via a new .bin file
    # VIPTELA Physical appliances will be upgraded via a new .tar.gz file

    viptela.result['changed'] = False

    vManage_software_list = viptela.get_software_images_list()

    if viptela.params['state'] == 'present':

        for software_to_upload in upload_software_list:

            try:
                present = False
                path_software_to_be_uploaded = software_to_upload['file']

                if not os.path.exists(path_software_to_be_uploaded):
                    module.fail_json(
                        msg="File does not exists")

                filename_software_to_be_uploaded = os.path.basename(path_software_to_be_uploaded)

                for software in vManage_software_list:
                    availabe_files_list = software["availableFiles"].split(', ')
                    if filename_software_to_be_uploaded in availabe_files_list:
                        present = True

                if not module.check_mode and not present:
                    response = viptela.request('/dataservice/device/action/software/package', method='POST',
                                               files={'file': open(path_software_to_be_uploaded, 'rb')},
                                               data={'validity': 'valid', 'upload': 'true'},
                                               headers=None)

                    viptela.result['changed'] = True
            except Exception as e:
                module.fail_json(
                    msg="General Error {0}".format(e))

    else:
        # absent to be added
        pass

    viptela.exit_json(**viptela.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
