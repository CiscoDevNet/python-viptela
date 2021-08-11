"""Cisco vManage Cluster API Methods.
"""

from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class Cluster(object):
    """vManage Cluster API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Cluster.

    """
    def __init__(self, session, host, port=443):
        """Initialize Cluster object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def get_cluster_connected_devices_list(self, vmanage_cluster_ip):
        """Obtain vManage cluster connected devices

        Args:
            vmanage_cluster_ip (str): vManage cluster interface IP address

        Returns:
            result (list): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/connectedDevices/{vmanage_cluster_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_health_details_list(self):
        """Obtain vManage cluster health details

        Args:
            None (None):

        Returns:
            result (list): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/health/details"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_health_status_list(self):
        """Obtain vManage cluster health status

        Args:
            None (None):

        Returns:
            result (list): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/health/status"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_list(self):
        """Obtain vManage cluster list

        Args:
            None (None):

        Returns:
            result (list): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/list"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_ip_addresses_dict(self):
        """Obtain vManage cluster IP addresses

        Args:
            None (None):

        Returns:
            result (dict): All data associated with a response.
        """

        result = {}
        vmanages = self.get_cluster_list()
        for vmanage in vmanages[0]['data']:
            vmanage_id = vmanage['vmanageID']
            url = f"{self.base_url}clusterManagement/iplist/{vmanage_id}"
            response = HttpMethods(self.session, url).request('GET')
            # result = ParseMethods.parse_data(response)
            result[vmanage_id] = response['json']
        return result

    def get_cluster_ready_state(self):
        """Obtain vManage cluster ready state

        Args:
            None (None):

        Returns:
            result (bool): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/isready"
        response = HttpMethods(self.session, url).request('GET')
        result = response['json']['isReady']
        # result = ParseMethods.parse_data(response)
        return result

    def get_cluster_node_properties(self):
        """Obtain connected vManage cluster node properties

        Args:
            None (None):

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/nodeProperties"
        response = HttpMethods(self.session, url).request('GET')
        result = response['json']
        # result = ParseMethods.parse_data(response)
        return result

    def get_cluster_tenancy_mode(self):
        """Obtain vManage cluster tenancy mode

        Args:
            None (None):

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/tenancy/mode"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_vmanage_details_list(self, vmanage_cluster_ip):
        """Obtain vManage cluster specific vManage details using cluster interface IP

        Args:
            vmanage_cluster_ip (str): vManage cluster interface IP address

        Returns:
            result (list): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/vManage/details/{vmanage_cluster_ip}"
        response = HttpMethods(self.session, url).request('GET', timeout=30)
        result = ParseMethods.parse_data(response)
        return result
