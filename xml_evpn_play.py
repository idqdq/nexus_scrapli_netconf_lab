from lxml import etree
import re 

et = etree.parse("evpn_data.xml")
#print(etree.tostring(et, pretty_print=True).decode())

# get existed vlans with vxlan (accEncap attribute) 
# and init evpn_data object
evpn_data = []
bd_list = et.xpath('.//BD-list[.//accEncap]')

for bd in bd_list:
    evpn = dict()
    evpn["vlan"] = bd.findtext("fabEncap").split("-")[1]
    evpn["vni"] = bd.findtext("accEncap").split("-")[1]
    evpn_data.append(evpn)
print(evpn_data)

# enrich evpn_data with svi opts like mtu and vrf
for item in evpn_data:    
    vlan = f'vlan{item["vlan"]}'
    svi = et.xpath(f'.//svi-items/If-list[.//id="{vlan}"]')[0]
    item["mtu"] = svi.findtext("mtu")
    vrf = svi.xpath('.//rtvrfMbr-items/tDn/text()')[0]
    item["vrf"] = re.split('[\[\]]', vrf)[1].split('=')[1].strip('\'')
print(evpn_data)

# enrich evpn_data with ipv4 data
for item in evpn_data:    
    vlan = f'vlan{item["vlan"]}'
    ipv4item = et.xpath(f'.//if-items/If-list[.//id="{vlan}"]')[0]
    item["ip_address"] = ipv4item.xpath('.//addr-items/Addr-list/addr/text()')
    
print(evpn_data)

# filter out l2vni's
vni_list = et.xpath('.//Nw-list[.//associateVrfFlag="false"]')

for vni in vni_list:
    print (f'vni: {vni.findtext("vni")}; mcast: {vni.findtext("mcastGroup")}')

