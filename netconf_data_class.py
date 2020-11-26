from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from tpl_evpn_xml import *
from ypath import ypath_system, ppxml

# set of evpn/vxlan related ypaths
ypath_vlan = "/bd-items/bd-items/BD-list[]/fabEncap=vlan-{vlan_id}"
ypath_svi = "/intf-items/svi-items/If-list[]/id=vlan{vlan_id}"
ypath_ipv4 = "/ipv4-items/inst-items/dom-items/Dom-list/name={vrf_name}/if-items/If-list[]/id=vlan{vlan_id}"
ypath_svianycast = "/hmm-items/fwdinst-items/if-items/FwdIf-list[]/id=vlan{vlan_id}"
ypath_nve = "/eps-items/epId-items/Ep-list/epId=1/nws-items/vni-items/Nw-list[]/vni={vni}"
ypath_evpn = "/evpn-items/bdevi-items/BDEvi-list[]/encap=vxlan-{vni}"

ypath_vlan_conf = ypath_vlan + "/name={vlan_name}/id={vlan_id}/BdState=active/adminSt=active/bridgeMode=mac/fwdCtrl=mdst-flood/fwdMode=bridge,route/mode=CE"
ypath_vxlan_conf = ypath_vlan + "/name={vlan_name}/id={vlan_id}/accEncap=vxlan-{vni}/BdState=active/adminSt=active/bridgeMode=mac/fwdCtrl=mdst-flood/fwdMode=bridge,route/mode=CE"
ypath_svi_conf = ypath_svi + "/mtu={mtu}/descr={description}/adminSt=up/rtvrfMbr-items/tDn=//System//inst-items//Inst-list[name='{vrf_name}']"
ypath_ipv4_conf = ypath_ipv4 + "/addr-items/Addr-list/addr={ip_address}"
ypath_svianycast_conf = ypath_svianycast + "/adminSt=enabled/mode=anycastGW"
ypath_nve_mgroup_conf = ypath_nve + "/mcastGroup={mgroup}"
ypath_nve_ir_conf = ypath_nve + "/IngRepl-items/proto=bgp"

ypath_evpn_conf = ypath_evpn + "/rd=rd:unknown:0:0/rttp-items/RttP-list/type=export/ent-items/RttEntry-list/rtt=route-target:unknown:0:0"
# ypath2xml() can't create xml with multiple leafs so we have to add 2nd list separately 
# note: there is no '[]' hooks in the ypath so that the default operation "merge" will be used
ypath_evpn_rtimport_conf = "/evpn-items/bdevi-items/BDEvi-list/encap=vxlan-{vni}/rd=rd:unknown:0:0/rttp-items/RttP-list/type=import/ent-items/RttEntry-list/rtt=route-target:unknown:0:0"


def check_ip_int(ip_address):
    try :
        IPv4Interface(ip_address)
    except ValueError:
        return False
        
    try: 
        IPv4Network(ip_address)
        return False
    except:
        return True


def check_ip_mcast(mgroup):
    try: 
        return IPv4Address(mgroup).is_multicast
    except:
        return False


@dataclass
class vlan_svi_data:
    # mandatory data
    vlan_id: int    
    # optional data (with defaults)
    ip_address: str = '' # can be blank for a remove operation but mandatory for a creating one
    vlan_name: str = ''
    mtu: int = 1500
    description: str = 'SVI created by netconf'
    vrf_name: str = 'default'    

    def __post_init__(self):
        pass        

    def get_rpc_create(self):
        if not self.vlan_name:
            self.vlan_name = 'VLAN' + str(self.vlan_id) 
        if not check_ip_int(self.ip_address):
            raise ValueError('Incorrect Interface IP address')        

        return (tpl_config_head + 
                tpl_bd_conf.format(vlan_id=self.vlan_id, vlan_name=self.vlan_name) +
                tpl_svi_conf.format(vlan_id=self.vlan_id, mtu=self.mtu, description=self.description, vrf_name=self.vrf_name, ip_address=self.ip_address) +                 
                tpl_config_tail)

    def get_rpc_get(self):
        return (tpl_system_head + 
                tpl_bd_get.format(vlan_id=self.vlan_id) +
                tpl_svi_get.format(vlan_id=self.vlan_id) +
                tpl_system_tail)

    def get_rpc_remove(self):
        return (tpl_config_head + 
                tpl_bd_remove.format(vlan_id=self.vlan_id) +
                tpl_svi_remove.format(vlan_id=self.vlan_id) +                
                tpl_config_tail)


@dataclass
class evpn_data:
    # mandatory data
    vlan_id: int
    vni: int
    # optional data (with defaults)
    ip_address: str = '' # can be blank for a remove operation but mandatory for a creating one
    vlan_name: str = ''
    mtu: int = 1500
    description: str = 'anycast SVI'
    vrf_name: str = 'Tenant-1'
    mgroup: str = ''
    supARP: bool = False

    
    def __post_init__(self):
        self.get_list = [ypath_vlan.format(vlan_id=self.vlan_id),
                        ypath_svi.format(vlan_id=self.vlan_id),
                        ypath_ipv4.format(vlan_id=self.vlan_id, vrf_name=self.vrf_name),
                        ypath_svianycast.format(vlan_id=self.vlan_id),
                        ypath_nve.format(vni=self.vni),
                        ypath_evpn.format(vni=self.vni)]      

    
    def get_rpc_create(self):
        if not self.vlan_name:
            self.vlan_name = 'l2VNI-' + str(self.vni) 

        if not check_ip_int(self.ip_address):
            raise ValueError('Incorrect Interface IP address')

        if self.mgroup:
            if not check_ip_mcast(self.mgroup):
                raise ValueError('Incorrect multicast group IP address')

        self.supARP = 'enabled' if self.supARP else 'off'

        return (tpl_config_head + 
                tpl_bd_vxlan_conf.format(vlan_id=self.vlan_id, vlan_name=self.vlan_name, vni=self.vni) +
                tpl_svi_anycast_conf.format(vlan_id=self.vlan_id, mtu=self.mtu, description=self.description, vrf_name=self.vrf_name, ip_address=self.ip_address) + 
                (tpl_nve_mcast_conf.format(vni=self.vni, mgroup=self.mgroup, supARP=self.supARP) if self.mgroup else tpl_nve_ingress_conf.format(vni=self.vni, supARP=self.supARP)) + 
                tpl_bgp_evpn_conf.format(vni=self.vni) + 
                tpl_config_tail)

    
    def get_rpc_get(self):
        return (tpl_system_head + 
                tpl_bd_get.format(vlan_id=self.vlan_id) +
                tpl_svi_get.format(vlan_id=self.vlan_id) +
                tpl_nve_get.format(vni=self.vni) +
                tpl_bgp_evpn_get.format(vni=self.vni) +
                tpl_system_tail)

    
    def get_rpc_remove(self):
        return (tpl_config_head + 
                tpl_bd_remove.format(vlan_id=self.vlan_id) +
                tpl_svi_remove.format(vlan_id=self.vlan_id) +
                tpl_nve_remove.format(vni=self.vni) +
                tpl_bgp_evpn_remove.format(vni=self.vni) +
                tpl_config_tail)

    
    def get_rpc_ypath_create(self):    
        if not self.vlan_name:
            self.vlan_name = 'l2VNI-' + str(self.vni) 

        if not check_ip_int(self.ip_address):
            raise ValueError('Incorrect Interface IP address')
        
        from re import sub
        self.ip_ = sub(r'/', '//', self.ip_address)  # <-- ypath2xml workaround 

        if self.mgroup:
            if not check_ip_mcast(self.mgroup):
                raise ValueError('Incorrect multicast group IP address')

        self.supARP = 'enabled' if self.supARP else 'off'      

        conf_list = [ypath_vxlan_conf.format(vlan_id=self.vlan_id, vlan_name=self.vlan_name, vni=self.vni),
                ypath_svi_conf.format(vlan_id=self.vlan_id, mtu=self.mtu, description=self.description, vrf_name=self.vrf_name),
                ypath_ipv4_conf.format(vlan_id=self.vlan_id, vrf_name=self.vrf_name, ip_address=self.ip_),
                ypath_svianycast_conf.format(vlan_id=self.vlan_id),
                ypath_nve_mgroup_conf.format(vni=self.vni, mgroup=self.mgroup),
                ypath_evpn_conf.format(vni=self.vni),
                ypath_evpn_rtimport_conf.format(vni=self.vni)]

        return "<config>" + ypath_system(conf_list, operation="replace") + "</config>"

    
    def get_rpc_ypath_get(self):        
        return ypath_system(self.get_list) 


    def get_rpc_ypath_remove(self):
        return "<config>" + ypath_system(self.get_list, operation="remove") + "</config>" 
     