###################### xml rpcs to config l2vni (evpn) on a cisco nexus swicthes via netconf ######################
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
#------------------------------------------------------------------------------------------------------------------
############################### xml rpcs to get data from cisco nexus switches via netconf ########################
# xpath = "/System/evpn-items/bdevi-items/BDEvi-list/encap=vxlan-10020"
# xmlns = "http://cisco.com/ns/yang/cisco-nx-os-device"
# xml = '<System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device"><evpn-items><bdevi-items><BDEvi-list><encap>vxlan-10020</encap></BDEvi-list></bdevi-items></evpn-items></System>'
def xpath2xml(xpath, xmlns=''):
    
    pl = xpath.split('/')

    xmls = f'<{pl[1]} xmlns="{xmlns}">'
    xmle = f'</{pl[1]}>'
     
    def _xpath2xml(pl):
        key = ''
        xmls = ''
        xmle = ''

        for i in range(len(pl)):
            elem = pl[i]
            if "=" in elem:
                elem,key = elem.split("=")
                xmls += f'<{elem}>{key}</{elem}>'
                break
            xmls += f'<{elem}>'
            xmle = f'</{elem}>' + xmle
     
        if key and i < len(pl)-1:
            return xmls + _xpath2xml(pl[(i+1)::]) + xmle #recursion
        else:
            return xmls + xmle
     
    return xmls + _xpath2xml(pl[2::]) + xmle

