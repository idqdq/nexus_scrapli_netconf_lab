# I. get xml from switch
from scrapli_netconf.driver import NetconfScrape
my_device = {
    "host": "192.168.99.91",
    "auth_username": "apiuser",
    "auth_password": "apipassword",
    "auth_strict_key": False,    
}

from ypath import ypath_system, strip_ns

vrf_name = "Tenant-1"
xmlns = "http://cisco.com/ns/yang/cisco-nx-os-device"

ypath_vlan = "/bd-items/bd-items/BD-list"
ypath_svi = "/intf-items/svi-items/If-list"
ypath_ipv4 = f"/ipv4-items/inst-items/dom-items/Dom-list/name={vrf_name}/if-items/If-list"
ypath_svianycast = "/hmm-items/fwdinst-items/if-items/FwdIf-list"
ypath_nve = "/eps-items/epId-items/Ep-list/epId=1/nws-items/vni-items/Nw-list"
ypath_evpn = "/evpn-items/bdevi-items/BDEvi-list"

# get evpns
ypath_list = [ypath_vlan, ypath_svi, ypath_ipv4, ypath_svianycast, ypath_nve, ypath_evpn]
rpc = ypath_system(ypath_list, xmlns)

with NetconfScrape(**my_device) as conn:
    response = conn.get(filter_=rpc, filter_type="subtree")

res = response.result

# II. play with the given xml
from lxml import etree
# convert the xml-like result (type string) to etree and strip namespaces
et = strip_ns(etree.fromstring(res))
xml_res = etree.tostring(et, pretty_print=True).decode()
print(xml_res)
# save xml to the file evpn_data.xml
with open("evpn_data.xml", "w") as f:
    f.write(xml_res)

# filter out l2vni's
vni_list = et.xpath('.//Nw-list[.//associateVrfFlag="false"]')

for vni in vni_list:
    print (f'vni: {vni.findtext("vni")}; mcast: {vni.findtext("mcastGroup")}')

