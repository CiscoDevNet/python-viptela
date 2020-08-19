"""Cisco vManage Authentication API Methods.
"""

from __future__ import (absolute_import, division, print_function)

import json
import requests
import urllib3
from vmanage.api.utilities import Utilities

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Authentication(object):
    """vManage Authentication API

    Responsible for retrieving the JSESSIONID after a username/password
    has been authenticated.  If the vManage version is >= 19.2.0 then
    the X-XSRF-TOKEN will be retrieved and added to the header.  An
    HTTP(S) Request session object will be returned.

    """
    def __init__(self, host=None, user=None, password=None, tenant=None, port=443, validate_certs=False, timeout=10):
        """Initialize Authentication object with session parameters.

        Args:
            host (str): hostname or IP address of vManage
            user (str): username for authentication
            password (str): password for authentication
            port (int): default HTTPS port 443
            validate_certs (bool): turn certificate validation
                on or off.
            timeout (int): how long Reqeusts will wait for a
                response from the server, default 10 seconds

        """

        self.host = host
        self.user = user
        self.password = password
        self.tenant = tenant
        self.port = port
        self.timeout = timeout
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.session = requests.Session()
        self.session.verify = validate_certs

    def login(self):
        """Executes login tasks against vManage to retrieve token(s).

        Args:
            None.

        Returns:
            self.session: a Requests session with JSESSIONID and an
            X-XSRF-TOKEN for vManage version >= 19.2.0.

        Raises:
            LoginFailure: If the username/password are incorrect.
            RequestException: If the host is not accessible.

        """

        try:
            api = 'j_security_check'
            url = f'{self.base_url}{api}'
            response = self.session.post(url=url,
                                         data={
                                             'j_username': self.user,
                                             'j_password': self.password
                                         },
                                         timeout=self.timeout)

            if (response.status_code != 200 or response.text.startswith('<html>')):
                raise Exception('Login failed, check user credentials.')

            version = Utilities(self.session, self.host, self.port).get_vmanage_version()

            if version >= '19.2.0':
                api = 'client/token'
                url = f'{self.base_url}{api}'
                response = self.session.get(url=url, timeout=self.timeout)
                self.session.headers['X-XSRF-TOKEN'] = response.content

            if self.tenant:
                api = 'tenant'
                url = f'{self.base_url}{api}'
                response = self.session.get(url=url, timeout=self.timeout)
                tenant_list = json.loads(response.content)['data']
                tenant_pair = dict((i['name'], i['tenantId']) for i in tenant_list)

                if self.tenant in tenant_pair:
                    tenant_id = tenant_pair[self.tenant]
                    api = f'tenant/{tenant_id}/switch'
                    url = f'{self.base_url}{api}'
                    response = self.session.post(url=url, timeout=self.timeout)

                    if (response.status_code != 200 or response.text.startswith('<html>')):
                        raise Exception('Tenant login failed, check user credentials.')

                    self.session.headers["VSessionId"] = json.loads(response.content)['VSessionId']
                else:
                    raise Exception('Tenant not found, check tenant name.')

        except requests.exceptions.RequestException as e:
            raise Exception(f'Could not connect to {self.host}: {e}')

        return self.session
