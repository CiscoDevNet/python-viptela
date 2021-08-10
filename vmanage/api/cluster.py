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

    def get_cluster_connected_devices(self, vmanage_cluster_ip):
        """Obtain vManage cluster connected devices

        Args:
            vmanage_cluster_ip (str): vManage cluster interface IP address

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/connectedDevices/{vmanage_cluster_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_health_details(self):
        """Obtain vManage cluster health details

        Args:
            None (None):

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/health/details"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_health_status(self):
        """Obtain vManage cluster health status

        Args:
            None (None):

        Returns:
            result (dict): All data associated with a response.
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
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}clusterManagement/list"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_cluster_ip_list(self):
        """Obtain vManage cluster ip list from all vManages

        Args:
            None (None):

        Returns:
            result (dict): All data associated with a response.
        """

        cluster_list = self.get_cluster_list()
        result = {}
        for vmanage in cluster_list[0]['data']:
            vmanage_id = vmanage['vmanageID']
            url = f"{self.base_url}clusterManagement/iplist/{vmanage_id}"
            response = HttpMethods(self.session, url).request('GET')
            cluster_ip_list = ParseMethods.parse_data(response)
            result[vmanage_id] = cluster_ip_list
        return result
