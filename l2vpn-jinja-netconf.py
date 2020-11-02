# test
# process data using jinja2 
conf_tpl="""
<config>
    <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
        <bd-items>
            <bd-items>
                <BD-list>
                    <fabEncap>vlan-{{ data.vlan_id }}</fabEncap>
                    <name>{{ data.vlan_name|default("VLAN" + data.vlan_id|string) }}</name>                    
                    <BdState>active</BdState>
                    <accEncap>vxlan-{{ data.vni }}</accEncap>
                    <adminSt>active</adminSt>
                    <bridgeMode>mac</bridgeMode>
                    <fwdCtrl>mdst-flood</fwdCtrl>
                    <fwdMode>bridge,route</fwdMode>
                    <id>{{ data.vlan_id }}</id>
                    <mode>CE</mode>
                </BD-list>
            </bd-items>
        </bd-items>
        <intf-items>
            <svi-items>
                <If-list>
                    <id>vlan{{ data.vlan_id }}</id>
                    <mtu>{{ mtu|default(1500) }}</mtu>                    
                    {{ "<descr>{}</descr>".format(data.description) if data.description }}
                    <adminSt>up</adminSt>
                    <rtvrfMbr-items>
                        <tDn>/System/inst-items/Inst-list[name='{{ data.vrf_name|default("Tenant-1") }}']</tDn>
                    </rtvrfMbr-items>
                    <vlanId>{{ data.vlan_id }}</vlanId>
                </If-list>
            </svi-items>
        </intf-items>
        <ipv4-items>
            <inst-items>
                <dom-items>
                    <Dom-list>
                        <name>{{ data.vrf_name|default("Tenant-1") }}</name>
                        <if-items>
                            <If-list>
                                <id>vlan{{ data.vlan_id }}</id>
                                <addr-items>
                                    <Addr-list>
                                        <addr>{{ data.ip_addr|default("10.1." + data.vlan_id|string + ".254/24") }}</addr>
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
                        <id>vlan{{ data.vlan_id }}</id>
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
                                <vni>{{ data.vni }}</vni>
                                {{ "<mcastGroup>{}</mcastGroup>".format(data.mgroup) if data.mgroup else "<IngRepl-items><proto>bgp</proto></IngRepl-items>" }}
                                {{ "<suppressARP>enabled</suppressARP>" if data.supARP }}
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
                    <encap>vxlan-{{ data.vni }}</encap>
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
</config>
"""

from jinja2 import Template

t = Template(conf_tpl)

data=dict(vlan_id=120, vni=10120)   

tt = t.render(data=data)

print(tt)
