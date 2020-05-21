"""Cisco vManage Certificate API Methods.
"""

import json
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
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
        """Generate CSR for device

        Args:
            device_ip (str): IP address of device.

        Returns:
            deviceCSR (str): The CSR for the device.
        """

        payload = {"deviceIP": device_ip}
        url = f"{self.base_url}generate/csr"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        result = ParseMethods.parse_data(response)
        return result[0]['deviceCSR']

    def install_device_cert(self, cert):
        """Install signed cert on vManage

        Args:
            cert (str): The certificate to install.

        Returns:
            id (str): The action ID of the install command.
        """

        url = f"{self.base_url}install/signedCert"
        response = HttpMethods(self.session, url).request('POST', payload=cert)
        utilities = Utilities(self.session, self.host)
        if 'json' in response and 'id' in response['json']:
            utilities.waitfor_action_completion(response['json']['id'])
        else:
            raise Exception('Did not get action ID after installing certificate.')
        return response['json']['id']

    def push_certificates(self):
        """Push certificates to all controllers

        Returns:
            id (str): The action ID of the push command.
        """

        url = f"{self.base_url}vedge/list?action=push"
        response = HttpMethods(self.session, url).request('POST', payload={})
        utilities = Utilities(self.session, self.host)

        if 'json' in response and 'id' in response['json']:
            utilities.waitfor_action_completion(response['json']['id'])
        else:
            raise Exception('Did not get action ID after pushing certificates.')
        return response['json']['id']

    def get_vmanage_root_cert(self):
        """Get vManage root certificate

        Args:

        Returns:
            rootcertificate (str): The root certificate.
        """

        url = f"{self.base_url}rootcertificate"
        response = HttpMethods(self.session, url).request('GET')
        try:
            return response['json']['rootcertificate']
        except:
            raise Exception('Error retrieving root certificate')
