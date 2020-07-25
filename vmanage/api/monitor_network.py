"""Cisco vManage Monitor Networks API Methods.
"""

from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods

CEDGE_LIST = ['vedge-CSR-1000v', 'vedge-ISR-4331',
              'vedge-ISR-4431', 'vedge-ISR-4461',
              'vedge-ISR-4451-X', 'vedge-IR-1101',
              'vedge-ISRv', 'vedge-ISR-4321',
              'vedge-ISR-4351', 'vedge-ISR-4221',
              'vedge-ISR-4221X', 'vedge-ASR-1001-X',
              'vedge-ASR-1002-X', 'vedge-ASR-1002-HX',
              'vedge-ASR-1001-HX', 'vedge-C1101-4P',
              'vedge-C1101-4PLTEP', 'vedge-C1111-4P',
              'vedge-C1161X-8P', 'vedge-C1111-8P',
              'vedge-C1121X-8P', 'vedge-C1111X-8P',
              'vedge-C1111-8PW', 'vedge-C1111-8PLTEEA',
              'vedge-C1121-8PLTEPW', 'vedge-C1111-8PLTELAW',
              'vedge-C1111-8PLTEEAW', 'vedge-C1111-8PLTELA',
              'vedge-C1111-4PLTEEA', 'vedge-C1101-4PLTEPW',
              'vedge-C1109-4PLTE2PW', 'vedge-C1109-4PLTE2P',
              'vedge-C1121X-8PLTE', 'vedge-C1161X-8PLTEP',
              'vedge-C1113-8PMLTEEA', 'vedge-C1111-4PLTELA',
              'vedge-C1116-4P', 'vedge-C1116-4PLTEEA',
              'vedge-C1117-4P', 'vedge-C1117-4PM',
              'vedge-C1117-4PLTEEA', 'vedge-C1126X-8PLTEP',
              'vedge-C1127X-8PLTEP', 'vedge-C1127X-8PMLTEP',
              'vedge-C1117-4PLTELA', 'vedge-C1117-4PMLTEEA']
VEDGE_LIST = ['vedge-cloud', 'vedge-100', 'vedge-100-B',
              'vedge-100-WM', 'vedge-100-M', 'vedge-1000',
              'vedge-2000', 'vedge-5000', 'vedge-ISR1100-4G',
              'vedge-ISR1100-4GLTE', 'vedge-ISR1100-6G']


class MonitorNetwork(object):
    """vManage Monitor Networks API

    Responsible for GET methods against vManage Real Time MonitoringI
    for network devices.

    """
    def __init__(self, session, host, port=443):
        """Initialize Monitor Networks object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def _get_device_type(self, system_ip):
        url = f"{self.base_url}device"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        device_model = [device['device-model'] for device in result if system_ip in device['system-ip']][0]

        url = f"{self.base_url}device/models"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        device_type = [device['templateClass'] for device in result if device_model in device['name']][0]
        return device_type

    def get_arp_table(self, system_ip):
        """Provides ARP entries for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/arp/sessions?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bfd_summary(self, system_ip):
        """Provides BFD summary for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/summary?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bfd_links(self, system_ip):
        """Provides BFD links for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/links?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bfd_history(self, system_ip):
        """Provides BFD history for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/history?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bfd_tloc(self, system_ip):
        """Provides BFD TLOC for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/tloc?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bfd_sessions(self, system_ip):
        """Provides BFD sessions for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/sessions?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bgp_routes(self, system_ip):
        """Provides BGP routes for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bgp/routes?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bgp_neighbors(self, system_ip):
        """Provides BGP neighbors for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bgp/neighbors?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bgp_summary(self, system_ip):
        """Provides BGP summary for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bgp/summary?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_summary(self, system_ip):
        """Provides current control summary for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/control/summary?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_connections(self, system_ip):
        """Provides current control connections for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/control/connections?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_connections_history(self, system_ip):
        """Provides control connections history for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/connectionshistory?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_valid_vsmarts(self, system_ip):
        """Provides control valid vsmarts for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/validvsmarts?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_valid_devices(self, system_ip):
        """Provides control valid devices for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/validdevices?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_wan_interface(self, system_ip):
        """Provides current control wan interface for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/waninterface?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_local_properties(self, system_ip):
        """Provides control local properties history for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/localproperties?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_links(self, system_ip):
        """Provides control links for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/control/links?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_wan_interface_color(self, system_ip):
        """Provides current control wan interface for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/waninterface/color?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_affinity_config(self, system_ip):
        """Provides current control affinity config for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/affinity/config?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_affinity_status(self, system_ip):
        """Provides current control affinity status for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/control/affinity/status?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_device_status(self, system_ip):
        """Provides status for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device?system-ip={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_device_system_info(self, system_ip):
        """Provides system info for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/system/info?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_dhcp_clients(self, system_ip):
        """Provides dhcp clients for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/dhcp/client?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_dhcp_interfaces(self, system_ip):
        """Provides dhcp interfaces for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/dhcp/interfaces?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_dhcp_servers(self, system_ip):
        """Provides dhcp servers for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/dhcp/servers?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ip_routetable(self, system_ip):
        """Provides OMP peers for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """
        
        device_type = self._get_device_type(system_ip)
        if device_type == 'cedge':
            url = f"{self.base_url}device/ip/ipRoutes?deviceId={system_ip}"
        elif device_type == 'vedge':
            url = f"{self.base_url}device/ip/routetable?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_omp_peers(self, system_ip):
        """Provides OMP peers for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/omp/peers?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_omp_routes_received(self, system_ip):
        """Provides OMP received routes for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/omp/routes/received?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_omp_routes_advertised(self, system_ip):
        """Provides OMP advertised routes for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/omp/routes/advertised?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_omp_summary(self, system_ip):
        """Provides OMP summary for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/omp/summary?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_orchestrator_summary(self, system_ip):
        """Provides orchestrator (vbond) summary for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/orchestrator/summary?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_orchestrator_connections(self, system_ip):
        """Provides orchestrator (vbond) connections for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/orchestrator/connections?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_orchestrator_connections_history(self, system_ip):
        """Provides orchestrator (vbond) connections history for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/orchestrator/connections?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_orchestrator_local_properties(self, system_ip):
        """Provides orchestrator (vbond) local properties history for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/orchestrator/localproperties?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_interfaces(self, system_ip):
        """Provides OSPF interfaces for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/ospf/interface?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_neighbors(self, system_ip):
        """Provides OSPF neighbors for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/ospf/neighbor?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_routes(self, system_ip):
        """Provides OSPF routes for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/ospf/routes?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_database(self, system_ip):
        """Provides OSPF database for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/ospf/database?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_database_summary(self, system_ip):
        """Provides OSPF database summary for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/ospf/databasesummary?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_process(self, system_ip):
        """Provides OSPF process for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/ospf/process?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_ospf_database_external(self, system_ip):
        """Provides OSPF database external for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}" \
              f"device/ospf/databaseexternal?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_vrrp(self, system_ip):
        """Provides VRRP entries for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/vrrp?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_eigrp_interface(self, system_ip):
        """Provides EIGRP interface for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/eigrp/interface?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_eigrp_route(self, system_ip):
        """Provides EIGRP route for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/eigrp/route?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_eigrp_topology(self, system_ip):
        """Provides EIGRP topology for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/eigrp/topology?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result
