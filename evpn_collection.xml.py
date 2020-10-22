# Netconf XML RPC for creating vlan + vni
#
# vlan 126
#   name Vlan126
#   nv-segment 10126
#
# (vlan_name, vlan_id, vni)
vlan_vni_conf="""
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
        <bd-items>
            <bd-items>
                <BD-list>
                    <fabEncap>vlan-{vlan_id}</fabEncap>
                    <name>{vlan_name}</name>
                    <BdState>active</BdState>
                    <accEncap>vxlan-{vni}</accEncap>
                    <adminSt>active</adminSt>
                    <bridgeMode>mac</bridgeMode>
                    <fwdCtrl>mdst-flood</fwdCtrl>
                    <fwdMode>bridge,route</fwdMode>
                    <id>{vlan_id}</id>
                    <longName>false</longName>
                    <macPacketClassify>disable</macPacketClassify>
                    <mode>CE</mode>
                    <xConnect>disable</xConnect>
                </BD-list>
            </bd-items>
        </bd-items>
    </System>
</config>"""


# Netconf XML RPC for creating SVI with anycast GW
#
# interface Vlan126
#   description svi126 by netconf
#   no shutdown
#   mtu 9000
#   vrf member Tenant-1
#   ip address 10.1.126.254/24
#   fabric forwarding mode anycast-gateway
#
# (vlan_id, desctiption, vrf_name, ip_addr)
svi_anycast_conf="""
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
        <intf-items>
            <svi-items>
                <If-list>
                    <id>vlan{vlan_id}</id>
                    <mtu>{mtu}</mtu>
                    <descr>{description}</descr>
                    <adminSt>up</adminSt>
                    <rtvrfMbr-items>
                        <tDn>/System/inst-items/Inst-list[name='{vrf_name}']</tDn>
                    </rtvrfMbr-items>
                    <vlanId>{vlan_id}</vlanId>
                </If-list>
            </svi-items>
        </intf-items>
        <ipv4-items>
            <inst-items>
                <dom-items>
                    <Dom-list>
                        <name>{vrf_name}</name>
                        <if-items>
                            <If-list>
                                <id>vlan{vlan_id}</id>
                                <addr-items>
                                    <Addr-list>
                                        <addr>{ip_addr}</addr>
                                    </Addr-list>
                                </addr-items>
                            </If-list>
                        </if-items>
                    </Dom-list>
                </dom-items>
            </inst-items>
        </ipv4-items>
        <hmm-items>
            <fwdinst-items>
                <if-items>
                    <FwdIf-list>
                        <id>vlan{vlan_id}</id>
                        <adminSt>enabled</adminSt>
                        <mode>anycastGW</mode>
                    </FwdIf-list>
                </if-items>
            </fwdinst-items>
        </hmm-items>
    </System>
</config>"""


# Netconf XML RPC to add vni into the nve1 interface with ingress protocol BGP and supress-arp
#
# interface nve1
#   member vni 10025
#     suppress-arp
#     ingress-replication protocol bgp
#
# variables (vni, supARP)
add_vni_to_nve1_conf = """
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
      <eps-items>
        <epId-items>
          <Ep-list>
            <epId>1</epId>
            <nws-items>
              <vni-items>
                <Nw-list>
                  <vni>{vni}</vni>
                  <IngRepl-items>
                    <proto>bgp</proto>
                  </IngRepl-items>  
                  <suppressARP>{supARP}</suppressARP>
                </Nw-list>
              </vni-items>
            </nws-items>
          </Ep-list>
        </epId-items>
      </eps-items>
    </System>
</config>"""


# Netconf XML RPC to add vni into bgp evpn config
# 
# evpn
#   vni 10020 l2
#     rd auto
#     route-target import auto
#     route-target export auto
#
# variables (vni)
add_vni_to_bgp_conf="""
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
        <evpn-items>
            <adminSt>enabled</adminSt>
            <bdevi-items>
                <BDEvi-list>
                    <encap>vxlan-{vni}</encap>
                    <rd>rd:unknown:0:0</rd>
                    <rttp-items>
                        <RttP-list>
                            <type>export</type>
                            <ent-items>
                                <RttEntry-list>
                                    <rtt>route-target:unknown:0:0</rtt>
                                </RttEntry-list>
                            </ent-items>
                        </RttP-list>
                        <RttP-list>
                            <type>import</type>
                            <ent-items>
                                <RttEntry-list>
                                    <rtt>route-target:unknown:0:0</rtt>
                                </RttEntry-list>
                            </ent-items>
                        </RttP-list>
                    </rttp-items>
                </BDEvi-list>
            </bdevi-items>
        </evpn-items>
	</System>
</config>"""


# Now lets combine all RPCs together to create an L3VNI at once
# Netconf XML RPC for creating a new vlan with a vni and related SVI with anycast GW and then to add that vni into the nve1 interface and into bgp evpn configs
#(vlan_id, vlan_name, vni, desctiption, vrf_name, ip_addr, supARP(off|enabled), mtu(default=1500))
# data=dict(vlan_name="VLAN125", vlan_id=125, vni=10025, desctiption="SVI 125 (via netconf)", vrf_name="Tenent-1", ip_address="10.1.125.0/24", supARP="enabled")
# str.format(vlan_name=data['vlan_name'], vlan_id=data['vlan_id'], vni=data['vni'], description=data['description'], vrf_name=data['vrf_name'], ip_address=data['ip_address'], supARP=data['supARP'], mtu=data.get("mtu", 1500))
add_l3vni_conf = """
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
        <bd-items>
            <bd-items>
                <BD-list>
                    <fabEncap>vlan-{vlan_id}</fabEncap>
                    <name>{vlan_name}</name>
                    <BdState>active</BdState>
                    <accEncap>vxlan-{vni}</accEncap>
                    <adminSt>active</adminSt>
                    <bridgeMode>mac</bridgeMode>
                    <fwdCtrl>mdst-flood</fwdCtrl>
                    <fwdMode>bridge,route</fwdMode>
                    <id>{vlan_id}</id>
                    <mode>CE</mode>
                </BD-list>
            </bd-items>
        </bd-items>
        <intf-items>
            <svi-items>
                <If-list>
                    <id>vlan{vlan_id}</id>
                    <mtu>{mtu}</mtu>
                    <descr>{description}</descr>
                    <adminSt>up</adminSt>
                    <rtvrfMbr-items>
                        <tDn>/System/inst-items/Inst-list[name='{vrf_name}']</tDn>
                    </rtvrfMbr-items>
                    <vlanId>{vlan_id}</vlanId>
                </If-list>
            </svi-items>
        </intf-items>
        <ipv4-items>
            <inst-items>
                <dom-items>
                    <Dom-list>
                        <name>{vrf_name}</name>
                        <if-items>
                            <If-list>
                                <id>vlan{vlan_id}</id>
                                <addr-items>
                                    <Addr-list>
                                        <addr>{ip_addr}</addr>
                                    </Addr-list>
                                </addr-items>
                            </If-list>
                        </if-items>
                    </Dom-list>
                </dom-items>
            </inst-items>
        </ipv4-items>
        <hmm-items>
            <fwdinst-items>
                <if-items>
                    <FwdIf-list>
                        <id>vlan{vlan_id}</id>
                        <adminSt>enabled</adminSt>
                        <mode>anycastGW</mode>
                    </FwdIf-list>
                </if-items>
            </fwdinst-items>
        </hmm-items>
        <eps-items>
            <epId-items>
                <Ep-list>
                    <epId>1</epId>
                    <nws-items>
                        <vni-items>
                            <Nw-list>
                                <vni>{vni}</vni>
                                <IngRepl-items>
                                    <proto>bgp</proto>
                                </IngRepl-items>
                                <suppressARP>{supARP}</suppressARP>
                            </Nw-list>
                        </vni-items>
                    </nws-items>
                </Ep-list>
            </epId-items>
        </eps-items>
        <evpn-items>
            <adminSt>enabled</adminSt>
            <bdevi-items>
                <BDEvi-list>
                    <encap>vxlan-{vni}</encap>
                    <rd>rd:unknown:0:0</rd>
                    <rttp-items>
                        <RttP-list>
                            <type>export</type>
                            <ent-items>
                                <RttEntry-list>
                                    <rtt>route-target:unknown:0:0</rtt>
                                </RttEntry-list>
                            </ent-items>
                        </RttP-list>
                        <RttP-list>
                            <type>import</type>
                            <ent-items>
                                <RttEntry-list>
                                    <rtt>route-target:unknown:0:0</rtt>
                                </RttEntry-list>
                            </ent-items>
                        </RttP-list>
                    </rttp-items>
                </BDEvi-list>
            </bdevi-items>
        </evpn-items>
    </System>
</config>"""