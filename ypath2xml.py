import re
import xml.dom.minidom

def ypath2xml(ypath, xmlns='', operation=None):
    #transforms xpath-like string (ypath) e.g. "/System/eps-items/epId-items/Ep-list/epId=1/nws-items/vni-items/Nw-list[]/vni=10444"
    #to xml-like sequence of elements tags: 
    # <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    #   <eps-items>
    #       <epId-items>
    #           <Ep-list>
    #               <epId>1</epId>
    #               <nws-items>
    #                   <vni-items>
    #                       <Nw-list operation="remove">
    #                           <vni>10444</vni>
    #                       </Nw-list>
    #                   </vni-items>
    #               </nws-items>
    #           </Ep-list>
    #       </epId-items>
    #   </eps-items>
    # </System>
    #
    # it has optional parameter 'operation' that adds the string 'operation="value"' to the element marked with square brackets '[]'
    # for an nxos the value of the operation can be either "remove" or "replace"for an nxo
    #
    # there is a problem with parsing elements that contain the '/' separator within like this tDn element has:
    # /System/intf-items/svi-items/If-list/rtvrfMbr-items/tDn=/System/inst-items/Inst-list[name='{vrf_name}']
    # the same case if you want to configure a physical interface like Eth103/1/20
    # 
    # as a workaround I mark all the slashes with additional one, then replace that doubleslashes with # sign
    # then split ypath and unmark them back

    ypath = re.sub(r'//', '#', ypath) # <-- replace doubleslashes with '#'
    pl = ypath.split('/')
    
    xmls = f'<{pl[1]} xmlns="{xmlns}">' if xmlns else f'<{pl[1]}>'
    xmle = f'</{pl[1]}>'
     
    def _ypath2xml(pl):
        key = ''
        xmls = ''
        xmle = ''
        operation_set = ("remove", "replace")
        
        for i in range(len(pl)):
            elem = pl[i]
            if "=" in elem:
                elem,key = elem.split("=", 1)
                key = re.sub(r'#', '/', key) # <-- replace '#' with '/'
                xmls += f'<{elem}>{key}</{elem}>'
                break
            
            if "[]" in elem:
                elem = elem[:-2]
                if operation:
                    if operation not in operation_set:
                        raise ValueError(f'Incorrect operation value\nmust be one of the following: {", ".join(operation_set)}')
                    xmls += f'<{elem} operation="{operation}">'                
                else:
                    xmls += f'<{elem}>'
            else:                    
                xmls += f'<{elem}>'
            xmle = f'</{elem}>' + xmle
     
        if key and i < len(pl)-1:
            return xmls + _ypath2xml(pl[(i+1)::]) + xmle #recursion
        else:
            return xmls + xmle
         
    return xmls + _ypath2xml(pl[2::]) + xmle

def ppxml(xmlstr):
    print(xml.dom.minidom.parseString(xmlstr).toprettyxml(indent="    "))

ypath = "/System/evpn-items/adminSt=enabled/bdevi-items/BDEvi-list/encap=vxlan-10010/rd=rd:unknown:0:0/rttp-items/RttP-list/type=export/ent-items/Rtt-Entry-list/rtt=route-target:unknown:0:0"

ppxml(ypath2xml(ypath, xmlns='blabla'))
