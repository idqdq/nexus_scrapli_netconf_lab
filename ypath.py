import re
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
    # operation values corresponds to RFC6241 https://tools.ietf.org/html/rfc6241#page-37
    #
    # there is a problem with parsing elements that contain the '/' separator within like this tDn element has:
    # /System/intf-items/svi-items/If-list/rtvrfMbr-items/tDn=/System/inst-items/Inst-list[name='{vrf_name}']
    # the same case if you want to configure a physical interface like Eth103/1/20
    # 
    # as a workaround I mark all the slashes with additional one, then replace that doubleslashes with # sign
    # then split ypath and unmark them back

    ypath = re.sub(r'//', '#', ypath) # <-- replace doubleslashes with '#'
    pl = ypath.split('/')
    
    xmls = f'<{pl[1]} xmlns:x="{xmlns}">' if xmlns else f'<{pl[1]}>'
    xmle = f'</{pl[1]}>'
     
    def _ypath2xml(pl):
        key = ''
        xmls = ''
        xmle = ''
        operation_set = ("merge", "replace", "create", "delete", "remove")        

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


# decorator is used to wrap xml with outer tags
from functools import wraps
def wrap_in_tag(tag, xmlns=None):
    xmls = f'<{tag} xmlns="{xmlns}">' if xmlns else f'<{tag}>'
    xmle = f'</{tag}>'    
    
    def decorator(func):        
        @wraps(func)
        def wrapped(*args, **kwargs):       
            if isinstance(args[0], str): 
                return xmls + f'{func(*args, **kwargs)}' + xmle
            if isinstance(args[0], list):
                return xmls + ''.join([func(ypath, **kwargs) for ypath in args[0]]) + xmle
            else:
                raise ValueError('ypath arg should be string or list of strings')
        return wrapped
    return decorator

@wrap_in_tag("config")
def ypath_config(ypath, xmlns='', operation=None):
    return ypath2xml(ypath, xmlns, operation)

@wrap_in_tag("System", "http://cisco.com/ns/yang/cisco-nx-os-device")
def ypath_system(ypath, xmlns='', operation=None):
    return ypath2xml(ypath, xmlns, operation)


# pretty print xml string
import xml.dom.minidom
def ppxml(xmlstr):    
    print(xml.dom.minidom.parseString(xmlstr).toprettyxml(indent="    "))


# helper function to strip ns from xml
# provided by Jeremy Shulman https://github.com/jeremyschulman/xml-tutorial/blob/master/strip-namespaces.md
from lxml import etree
def strip_ns(root: etree.Element) -> etree.Element:
    """
    This function removes all namespace information from an XML Element tree
    so that a Caller can then use the `xpath` function without having
    to deal with the complexities of namespaces.
    """

    # first we visit each node in the tree and set the tag name to its localname
    # value; thus removing its namespace prefix

    for elem in root.getiterator():
        elem.tag = etree.QName(elem).localname

    # at this point there are no tags with namespaces, so we run the cleanup
    # process to remove the namespace definitions from within the tree.

    etree.cleanup_namespaces(root)
    return root