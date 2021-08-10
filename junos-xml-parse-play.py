
#%%
from lxml import etree
import re 
from pprint import pprint
from ypath import strip_ns

#et = etree.parse("rpc-reply.xml")
#et = strip_ns(et)

xmlstr = '<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos">\n    <route-information xmlns="http://xml.juniper.net/junos/12.1X46/junos-routing">\n        <!-- keepalive -->\n        <route-table>\n            <table-name>inet.0</table-name>\n            <destination-count>451</destination-count>\n            <total-route-count>599</total-route-count>\n            <active-route-count>402</active-route-count>\n            <holddown-route-count>0</holddown-route-count>\n            <hidden-route-count>49</hidden-route-count>\n            <rt junos:style="brief">\n                <rt-destination>0.0.0.0/0</rt-destination>\n                <rt-entry>\n                    <active-tag>*</active-tag>\n                    <current-active/>\n                    <last-active/>\n                    <protocol-name>Static</protocol-name>\n                    <preference>5</preference>\n                    <age junos:seconds="27744094">45w6d 02:41:34</age>\n                    <nh>\n                        <selected-next-hop/>\n                        <to>212.113.97.1</to>\n                        <via>fe-0/0/2.0</via>\n                    </nh>\n                </rt-entry>\n                <rt-entry>\n                    <active-tag> </active-tag>\n                    <protocol-name>BGP</protocol-name>\n                    <preference>8</preference>\n                    <age junos:seconds="876198">1w3d 03:23:18</age>\n                    <local-preference>200</local-preference>\n                    <as-path>20632 31133 25159 65000 I</as-path>\n                    <nh>\n                        <selected-next-hop/>\n                        <to>172.17.78.34</to>\n                        <via>ge-0/0/0.0</via>\n                    </nh>\n                </rt-entry>\n                <rt-entry>\n                    <active-tag> </active-tag>\n                    <protocol-name>OSPF</protocol-name>\n                    <preference>150</preference>\n                    <age junos:seconds="866390">1w3d 00:39:50</age>\n                    <metric>100</metric>\n                    <rt-tag>0</rt-tag>\n                    <nh>\n                        <selected-next-hop/>\n                        <via>st0.0</via>\n                    </nh>\n                </rt-entry>\n            </rt>\n        </route-table>\n    </route-information>\n    <cli>\n        <banner></banner>\n    </cli>\n</rpc-reply>'
et = strip_ns(etree.fromstring(xmlstr))

print(etree.tostring(et, pretty_print=True).decode())

iface = et.xpath(".//rt-entry/nh")[0].findtext("via")

if (iface):
    print(iface)



# %%
