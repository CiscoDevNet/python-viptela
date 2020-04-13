"""Cisco vManage Certificate API Methods.
"""

from vmanage.api.http_methods import HttpMethods
from vmanage.api.utilities import Utilities


class Certificate(object):
    """vManage Certificate API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Certificates.

    """
    def __init__(self, session, host, port=443):
        """Initialize Device Inventory object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/certificate/'

    def generate_csr(self, device_ip):
        payload = {"deviceIP": device_ip}
        response = self.request('/dataservice/certificate/generate/csr', method='POST', payload=payload)

        if response.json:
            try:
                return response.json['data'][0]['deviceCSR']
            except Exception:  # TODO: figure out correct type to catch
                return None
        else:
            return None

    def install_device_cert(self, cert):
        response = self.request('/dataservice/certificate/install/signedCert', method='POST', data=cert)
        if response.json and 'id' in response.json:
            self.waitfor_action_completion(response.json['id'])
        else:
            self.fail_json(msg='Did not get action ID after attaching device to template.')
        return response.json['id']

    def push_certificates(self):
        """Push certificates to all controllers

        Returns:
            result (str): The action ID of the push command.
        """

        url = f"{self.base_url}vedge/list?action=push"
        response = HttpMethods(self.session, url).request('POST', payload={})
        utilities = Utilities(self.session, self.host)

        if 'json' in response and 'id' in response['json']:
            utilities.waitfor_action_completion(response['json']['id'])
        else:
            raise Exception('Did not get action ID after pushing certificates.')
        return response['json']['id']
