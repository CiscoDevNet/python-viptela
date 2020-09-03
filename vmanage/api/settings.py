"""Cisco vManage Settings API Methods.
"""

import json
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class Settings(object):
    """vManage Settings API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Settings.

    """
    def __init__(self, session, host, port=443):
        """Initialize vManage Settings object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/settings/configuration/'

    def get_vmanage_org(self):
        """Get vManage organization

        Args:

        Returns:
            org (str): The vManage organization.
        """

        url = f"{self.base_url}organization"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        if 'org' in result[0]:
            return result[0]['org']
        return None

    def set_vmanage_org(self, org):
        """Set vManage organization

        Args:
            org (str): The organization name to set.

        Returns:
            result (dict): The result of the POST operation
        """

        payload = {'org': org}
        url = f"{self.base_url}organization"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        result = ParseMethods.parse_data(response)
        return result[0]

    def get_vmanage_vbond(self):
        """Get vBond

        Args:
            
        Returns:
            result (dict): The result of the GET operation.
        """

        url = f"{self.base_url}device"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        if 'domainIp' in result[0]:
            return result[0]
        return {'domainIp': None, 'port': None}

    def set_vmanage_vbond(self, vbond, vbond_port='12346'):
        """Set vBond

        Args:
            vbond (str): The vBond IP address.
            vbond_port (str): The vBond port.

        Returns:
            result (dict): The result of the POST operation.
        """

        payload = {'domainIp': vbond, 'port': vbond_port}
        url = f"{self.base_url}device"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        result = ParseMethods.parse_data(response)
        return result[0]

    def get_vmanage_ca_type(self):
        """Get vManage CA type

        Args:

        Returns:
            certificateSigning (str): The CA type.
        """

        url = f"{self.base_url}certificate"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result[0]['certificateSigning']

    def set_vmanage_ca_type(self, ca_type):
        """Set vManage CA type

        Args:
            ca_type (str): The CA type.

        Returns:
            result (dict): The result of the POST operation.
        """

        payload = {'certificateSigning': ca_type, 'challengeAvailable': 'false'}
        url = f"{self.base_url}certificate"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        result = ParseMethods.parse_data(response)
        return result[0]

    def set_vmanage_root_cert(self, cert):
        """Set vManage root certiticate

        Args:
            cert (str): The root certiticate.

        Returns:
        """

        payload = {'enterpriseRootCA': cert}
        url = f"{self.base_url}certificate/enterpriserootca"
        response = HttpMethods(self.session, url).request('PUT', payload=json.dumps(payload))
        result = ParseMethods.parse_data(response)
        return result[0]

    def get_vmanage_banner(self):
        """Get vManage Banner

                Args:

                Returns:
                    bannerDetail (str): The banner for vmanage.
                """

        # banner = self.get('settings/configuration/banner')
        # if banner.status_code not in HTTP_SUCCESS_CODES:
        #     return "Error retrieving banner.  Status: {0} Error: {1}".format(banner.status_code, banner.text)
        # return banner.json()['data'][0]['bannerDetail']

        url = f"{self.base_url}banner"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result[0]['bannerDetail']
