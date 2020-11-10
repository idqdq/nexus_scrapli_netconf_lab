### netconf xml rpc templates for configuring l2vni (evpn) with anycast SVI on a cisco nexus swicthes via netconf ###
tpl_head = """
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">"""

tpl_tail = """
    </System>
</config>"""

tpl_bd_items = """
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
    </bd-items>"""

tpl_anycast_svi = """
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
                                    <addr>{ip_address}</addr>
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
    </hmm-items>"""

tpl_nve_mcast_repl = """
    <eps-items>
        <epId-items>
            <Ep-list>
                <epId>1</epId>
                <nws-items>
                    <vni-items>
                        <Nw-list>
                            <vni>{vni}</vni>
                            <mcastGroup>{mgroup}</mcastGroup>                                
                            <suppressARP>{supARP}</suppressARP>
                        </Nw-list>
                    </vni-items>
                </nws-items>
            </Ep-list>
        </epId-items>
    </eps-items>"""

tpl_nve_ingress_repl_bgp = """
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
    </eps-items>"""

tpl_bgp_evpn = """
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
    </evpn-items>"""
