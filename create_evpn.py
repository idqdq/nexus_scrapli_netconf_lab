from ypath import ppxml
from netconf_data_class import evpn_data, get_all_evpn_config_rpc
from nr_scrapli_funcs import nr_netconf_edit, nr_netconf_get
from evpn_xml_parse import get_evpn_data_from_xml
import pprint


def print_all_evpns():
    get_all_xml = get_all_evpn_config_rpc(vrf="Tenant-1")
    data = nr_netconf_get(filter_=get_all_xml, site="site1")
    pprint.pprint(data)

evpn444 = evpn_data(444, 10444, '10.4.4.4/24', mtu=3000, mgroup='230.4.4.4')
create_xml = evpn444.get_rpc_ypath_create()
get_xml = evpn444.get_rpc_ypath_get()
delete_xml = evpn444.get_rpc_ypath_remove()

#show initial state
print_all_evpns()

#create new evpn
nr_netconf_edit(create_xml, site="site1")
print_all_evpns()

#delete the new evpn
nr_netconf_edit(delete_xml, site="site1")
print_all_evpns()
