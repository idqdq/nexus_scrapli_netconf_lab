from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [    
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/getEvpnAll")
async def getEvpnAll():
    return {
        "evpnData": [
            {"vlan_id":"10","vni":"10010","vlan_name":"","svi_ip":"","svi_descr":"","mtu":"","vrf":"","mgroup":"","arpsup":True},
            {"vlan_id":"20","vni":"10020","vlan_name":"","svi_ip":"","svi_descr":"","mtu":"","vrf":"","mgroup":"","arpsup":False},
            {"vlan_id":"30","vni":"10030","vlan_name":"Vlan30","svi_ip":"10.1.30.254/24","svi_descr":"","mtu":"1600","vrf":"Tenant-1","mgroup":"231.0.0.30","arpsup":True},
            ]
    }
