"""Cisco vManage Monitor Networks API Methods.
"""

from six.moves.urllib.parse import urlencode
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class MonitorNetwork(object):
    """vManage Monitor Networks API

    Responsible for GET methods against vManage Real Time Monitoring
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
        device_model = self.get_device_system_info(system_ip)[0]['device-model']
        url = f"{self.base_url}device/models"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        device_type = [device['deviceClass'] for device in result if device_model in device['name']][0]
        return device_type

    def get_arp_table(self, system_ip):
        """Provides ARP entries for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/arp?deviceId={system_ip}"
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

    def get_bfd_links(self, system_ip, **kwargs):
        """Provides BFD links for device.

        Args:
            system_ip (str): Device System IP
            state (str): State

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/links"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'state' in kwargs:
            query_params.append(('state', kwargs['state']))
        if query_params:
            url += '?' + urlencode(query_params)
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

    def get_bfd_sessions(self, system_ip, **kwargs):
        """Provides BFD sessions for device.

        Args:
            system_ip (str): Device System IP
            remote_system_ip (str): Remote System IP
            remote_color (str): Remote Color
            local_color (str): Local Color

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bfd/sessions"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'remote_system_ip' in kwargs:
            query_params.append(('system-ip', kwargs['remote_system_ip']))
        if 'remote_color' in kwargs:
            query_params.append(('color', kwargs['remote_color']))
        if 'local_color' in kwargs:
            query_params.append(('local-color', kwargs['local_color']))
        if query_params:
            url += '?' + urlencode(query_params)
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_bgp_routes(self, system_ip, **kwargs):
        """Provides BGP routes for device.

        Args:
            system_ip (str): Device System IP
            vpn-id (str): VPN ID
            prefix (str): IP prefix
            nexthop (str): Nexthop

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bgp/routes"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'vpn_id' in kwargs:
            query_params.append(('vpn-id', kwargs['vpn_id']))
        if 'prefix' in kwargs:
            query_params.append(('prefix', kwargs['prefix']))
        if 'nexthop' in kwargs:
            query_params.append(('nexthop', kwargs['nexthop']))
        if query_params:
            url += '?' + urlencode(query_params)
        response = HttpMethods(self.session, url).request('GET', timeout=60)
        result = ParseMethods.parse_data(response)
        return result

    def get_bgp_neighbors(self, system_ip, **kwargs):
        """Provides BGP neighbors for device.

        Args:
            system_ip (str): Device System IP
            vpn-id (str): VPN ID
            peer-addr (str): Peer address
            as (str): ASN

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/bgp/neighbors"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'vpn_id' in kwargs:
            query_params.append(('vpn-id', kwargs['vpn_id']))
        if 'peer_addr' in kwargs:
            query_params.append(('peer-addr', kwargs['peer_addr']))
        if 'asn' in kwargs:
            query_params.append(('as', kwargs['asn']))
        if query_params:
            url += '?' + urlencode(query_params)
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

    def get_control_connections(self, system_ip, **kwargs):
        """Provides current control connections for device.

        Args:
            system_ip (str): Device System IP
            peer_type (str): Peer type (vedge, vsmart, vmanage, vbond)
            peer_system_ip (str): Peer System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/control/connections"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'peer_type' in kwargs:
            query_params.append(('peer-type', kwargs['peer_type']))
        if 'peer_system_ip' in kwargs:
            query_params.append(('system-ip', kwargs['peer_system_ip']))
        if query_params:
            url += '?' + urlencode(query_params)
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_control_connections_history(self, system_ip, **kwargs):
        """Provides control connections history for device.

        Args:
            system_ip (str): Device System IP
            peer_type (str): Peer type (vedge, vsmart, vmanage, vbond)
            peer_system_ip (str): Peer System IP
            local_color (str): Local Color

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/control/connectionshistory"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'peer_type' in kwargs:
            query_params.append(('peer-type', kwargs['peer_type']))
        if 'peer_system_ip' in kwargs:
            query_params.append(('system-ip', kwargs['peer_system_ip']))
        if 'local_color' in kwargs:
            query_params.append(('local-color', kwargs['local_color']))
        if query_params:
            url += '?' + urlencode(query_params)
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

    def get_control_links(self, system_ip, **kwargs):
        """Provides control links for device.

        Args:
            system_ip (str): Device System IP
            state (str): State

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/control/links"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'state' in kwargs:
            query_params.append(('state', kwargs['state']))
        if query_params:
            url += '?' + urlencode(query_params)
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

        url = f"{self.base_url}device/system/status?deviceId={system_ip}"
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

    def get_ip_route_table(self, system_ip, **kwargs):
        """Provides route table for device.

        Args:
            system_ip (str): Device System IP
            vpn_id (str): VPN ID
            address_family (str): Address Family
            destination_prefix (str): Destination Prefix
            source_protocol (str): Source Protocol
            next_hop_address (str): Next-Hop Address (cEdge Only)
            next_hop_oif (str): Next-Hop Outgoing Interface (cEdge Only)

        Returns:
            result (dict): All data associated with a response.
        """

        device_type = self._get_device_type(system_ip)
        if device_type == 'cisco-router':
            url = f"{self.base_url}device/ip/ipRoutes"
            query_params = []
            query_params.append(('deviceId', system_ip))
            if 'vpn_id' in kwargs:
                query_params.append(('routing-instance-name', kwargs['vpn_id']))
            if 'address_family' in kwargs:
                query_params.append(('rib-address-family', kwargs['address_family']))
            if 'destination_prefix' in kwargs:
                query_params.append(('route-destination-prefix', kwargs['destination_prefix']))
            if 'source_protocol' in kwargs:
                query_params.append(('route-source-protocol', kwargs['source_protocol']))
            if 'next_hop_address' in kwargs:
                query_params.append(('next-hop-next-hop-address', kwargs['next_hop_address']))
            if 'next_hop_oif' in kwargs:
                query_params.append(('next-hop-outgoing-interface', kwargs['next_hop_oif']))
        elif device_type == 'viptela-router':
            url = f"{self.base_url}device/ip/routetable"
            query_params = []
            query_params.append(('deviceId', system_ip))
            if 'vpn_id' in kwargs:
                query_params.append(('vpn-id', kwargs['vpn_id']))
            if 'address_family' in kwargs:
                query_params.append(('address-family', kwargs['address_family']))
            if 'destination_prefix' in kwargs:
                query_params.append(('prefix', kwargs['destination_prefix']))
            if 'source_protocol' in kwargs:
                query_params.append(('protocol', kwargs['source_protocol']))
        else:
            raise Exception(f"Could not retrieve device type {device_type} for {system_ip}")
        if query_params:
            url += '?' + urlencode(query_params)
        response = HttpMethods(self.session, url).request('GET', timeout=60)
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

    def get_omp_routes_received(self, system_ip, **kwargs):
        """Provides OMP received routes for device.

        Args:
            system_ip (str): Device System IP
            vpn_id (str): VPN ID
            prefix (str): Prefix

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/omp/routes/received"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'vpn_id' in kwargs:
            query_params.append(('vpn-id', kwargs['vpn_id']))
        if 'prefix' in kwargs:
            query_params.append(('prefix', kwargs['prefix']))
        if query_params:
            url += '?' + urlencode(query_params)
        response = HttpMethods(self.session, url).request('GET', timeout=60)
        result = ParseMethods.parse_data(response)
        return result

    def get_omp_routes_advertised(self, system_ip, **kwargs):
        """Provides OMP advertised routes for device.

        Args:
            system_ip (str): Device System IP
            vpn_id (str): VPN ID
            prefix (str): Prefix

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/omp/routes/advertised"
        query_params = []
        query_params.append(('deviceId', system_ip))
        if 'vpn_id' in kwargs:
            query_params.append(('vpn-id', kwargs['vpn_id']))
        if 'prefix' in kwargs:
            query_params.append(('prefix', kwargs['prefix']))
        if query_params:
            url += '?' + urlencode(query_params)
        response = HttpMethods(self.session, url).request('GET', timeout=60)
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
        response = HttpMethods(self.session, url).request('GET', timeout=60)
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

        device_type = self._get_device_type(system_ip)
        if device_type == 'viptela-router':
            url = f"{self.base_url}device/ospf/process?deviceId={system_ip}"
        elif device_type == 'cisco-router':
            raise Exception(f"OSPF Interface API endpoint not supported for device type {device_type} for {system_ip}")
        else:
            raise Exception(f"Could not retrieve device type {device_type} for {system_ip}")

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

    def get_eigrp_interfaces(self, system_ip):
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

    def get_eigrp_routes(self, system_ip):
        """Provides EIGRP route for device.

        Args:
            system_ip (str): Device System IP

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}device/eigrp/route?deviceId={system_ip}"
        response = HttpMethods(self.session, url).request('GET', timeout=60)
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
