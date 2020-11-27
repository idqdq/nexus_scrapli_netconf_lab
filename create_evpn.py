from ypath import ppxml
from netconf_data_class import evpn_data
from nr_scrapli_funcs import nr_netconf_edit

evpn333 = evpn_data(333, 10333, '10.3.3.3/24', mtu=3000, mgroup='230.3.3.3')

create_xml = evpn333.get_rpc_ypath_create()
get_xml = evpn333.get_rpc_ypath_get()
delete_xml = evpn333.get_rpc_ypath_remove()

nr_netconf_edit(create_xml, site="site1")
breakpoint()
nr_netconf_edit(delete_xml, site="site1")