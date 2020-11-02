from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from tpl_evpn_xml import *

@dataclass
class evpn_data:
    # mandatory data
    vlan_id: int
    vni: int
    ip_address: str
    # optional data (with defaults)
    vlan_name: str = ''
    mtu: int = 1500
    description: str = 'anycast SVI'
    vrf_name: str = 'Tenant-1'
    mgroup: str = ''
    supARP: bool = False

    def __check_ip_int(self):
        try :
            IPv4Interface(self.ip_address)
        except ValueError:
            return False
            
        try: 
            IPv4Network(self.ip_address)
            return False
        except:
            return True

    def __check_ip_mcast(self):
        try: 
            return IPv4Address(self.mgroup).is_multicast
        except:
            return False

    def __post_init__(self):
        if not self.vlan_name:
            self.vlan_name = 'l2VNI-' + str(self.vni) 
        if not self.__check_ip_int():
            raise ValueError('Incorrect Interface IP address')
        if self.mgroup:
            if not self.__check_ip_mcast():
                raise ValueError('Incorrect multicast group IP address')
        self.supARP = 'enabled' if self.supARP else 'off'

    def get_rpc(self):
            return (tpl_head + 
                tpl_bd_items.format(vlan_id=self.vlan_id, vlan_name=self.vlan_name, vni=self.vni) +
                tpl_anycast_svi.format(vlan_id=self.vlan_id, mtu=self.mtu, description=self.description, vrf_name=self.vrf_name, ip_address=self.ip_address) + 
                (tpl_nve_mcast_repl.format(vni=self.vni, mgroup=self.mgroup, supARP=self.supARP) if self.mgroup else tpl_nve_ingress_repl_bgp.format(vni=self.vni, supARP=self.supARP)) + 
                tpl_bgp_evpn.format(vni=self.vni) + 
                tpl_tail)