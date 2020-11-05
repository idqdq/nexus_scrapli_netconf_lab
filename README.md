# NXOS NetConf XML RPC lab

This lab is intended to figure out how to interract with NXOS switched via netconf

The goal is to craft and test RPCs that can be used in the evpn fabric controller (nxos only) that I plan to implement in the future


The tricky part is to dig around YANG models. There are three utilities that helps a lot:  
1. [pyang](https://github.com/mbj4668/pyang)
2. [gnmic prompt mode](https://gnmic.kmrd.dev/advanced/prompt_suggestions/)
3. [yang path explorer](https://github.com/hellt/yangpath)


