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

# enrich evpn_data with svi options: mtu, vrf, descr
# ipv4 options: ip_address
# hmm options: anycastGW
# eps options (nve1): mcastGroup, suppressARP 
# evpn options (rd/rt): rd, rtt_import, rtt_export
for item in evpn_data:    
    vlan = f'vlan{item["vlan"]}'
    vni = item["vni"]
    vxlan = f'vxlan-{vni}'

    svi = et.xpath(f'.//svi-items/If-list[.//id="{vlan}"]')[0]
    item["mtu"] = svi.findtext("mtu")
    vrf = svi.xpath('.//rtvrfMbr-items/tDn/text()')[0]
    item["vrf"] = re.split(r'[\[\]]', vrf)[1].split('=')[1].strip('\'')    
    descr = svi.findtext("descr")
    if descr:
        item["descr"] = descr

    ipv4item = et.xpath(f'.//if-items/If-list[.//id="{vlan}"]')[0]
    ip_address = ipv4item.xpath('.//addr-items/Addr-list/addr/text()')
    if ip_address:
        item["ip_address"] = ip_address[0]
    
    hmm = et.xpath(f'.//hmm-items/fwdinst-items/if-items/FwdIf-list[id="{vlan}" and mode="anycastGW"]')    
    if hmm:
        item["anycastGW"] = True

    eps = et.xpath(f'.//eps-items/epId-items/Ep-list[epId=1]/nws-items/vni-items/Nw-list[vni={vni} and associateVrfFlag="false"]')
    if eps:
        item["mcastGroup"] = eps[0].findtext("mcastGroup")
        item["suppressARP"] = eps[0].findtext("suppressARP")

    evpn = et.xpath(f'.//evpn-items/bdevi-items/BDEvi-list[encap="{vxlan}"]')
    if evpn:
        item["rd"] = evpn[0].findtext("rd")
        item["rtt_import"] = evpn[0].xpath('.//rttp-items/RttP-list[type="import"]/ent-items/RttEntry-list/rtt/text()')
        item["rtt_export"] = evpn[0].xpath('.//rttp-items/RttP-list[type="export"]/ent-items/RttEntry-list/rtt/text()')
        

# adding outer indexes like evpn20 for vlan20 
evpn_data = [ {f'evpn{item["vlan"]}':item } for item in evpn_data]        
from pprint import pprint
pprint(evpn_data)

