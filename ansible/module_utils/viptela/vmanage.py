from ansible.module_utils.basic import AnsibleModule, json, env_fallback
from vmanage.api.authentication import Authentication


def vmanage_argument_spec():
    return dict(host=dict(type='str', required=True, fallback=(env_fallback, ['VMANAGE_HOST'])),
                port=dict(type='str', required=False, fallback=(env_fallback, ['VMANAGE_PORT'])),
                user=dict(type='str', required=True, fallback=(env_fallback, ['VMANAGE_USERNAME'])),
                password=dict(type='str', required=True, fallback=(env_fallback, ['VMANAGE_PASSWORD'])),
                validate_certs=dict(type='bool', required=False, default=False),
                timeout=dict(type='int', default=30)
                )


class Vmanage(object):

    def __init__(self, module, function=None):
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.params['force_basic_auth'] = True
        self.username = self.params['user']
        self.password = self.params['password']
        self.host = self.params['host']
        self.port = self.params['port']
        self.timeout = self.params['timeout']

        self.__auth = None

    @property
    def auth(self):
        if self.__auth is None:
            self.__auth = Authentication(host=self.host, user=self.username, password=self.password).login()
        return self.__auth

    def exit_json(self, **kwargs):
        # self.logout()
        """Custom written method to exit from module."""

        self.result.update(**kwargs)
        self.module.exit_json(**self.result)

    def fail_json(self, msg, **kwargs):
        # self.logout()
        """Custom written method to return info on failure."""

        self.result.update(**kwargs)
        self.module.fail_json(msg=msg, **self.result)
