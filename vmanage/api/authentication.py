"""Cisco vManage Authentication API Methods.
"""

from __future__ import (absolute_import, division, print_function)

import requests
import urllib3
from random import randint
from vmanage.api.utilities import Utilities

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Authentication(object):
    """vManage Authentication API

    Responsible for retrieving the JSESSIONID after a username/password
    has been authenticated.  If the vManage version is >= 19.2.0 then
    the X-XSRF-TOKEN will be retrieved and added to the header.  An
    HTTP(S) Request session object will be returned.

    """
    def __init__(self, host=None, user=None, password=None, port=443, validate_certs=False, timeout=10):
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
        self.port = port
        self.timeout = timeout
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.session = requests.Session()
        self.session.verify = validate_certs

    def __enter__(self):
        self.login()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

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
                raise ConnectionError('Login failed, check user credentials.')

            version = Utilities(self.session, self.host, self.port).get_vmanage_version()

            if version >= '19.2.0':
                api = 'client/token'
                url = f'{self.base_url}{api}'
                response = self.session.get(url=url, timeout=self.timeout)
                self.session.headers['X-XSRF-TOKEN'] = response.content

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'Could not connect to {self.host}: {e}')

        return self.session

    def logout(self, session=None):
        """Executes a logout query against the vManage to terminate session.

        Args:
            Session: Optionally pass in a session if the login function was run directly.
            If no session is passed in, the logout operation is performed on self.session

        Returns:
            session: Returns the same session object after the logout functionality
            has been performed.

        Raises:
            ConnectionError if failure to connect to vManage for logout query.
        """
        try:
            if not session:
                session = self.session

            version = Utilities(session, self.host, self.port).get_vmanage_version()
            api = f"logout?nocache={randint(1,999)}"
            url = f'https://{self.host}:{self.port}/{api}'
            response = session.get(url=url, timeout=self.timeout)
            if response.status_code != 200:
                raise ConnectionError('Logout operation failed. Recieved non-200 code from vManage')
            if version >= '19.2.0':
                session.headers.pop('X-XSRF-TOKEN', None)

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'Could not connect to {self.host}: {e}')

        return session
