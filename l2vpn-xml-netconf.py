# play with data_class and scrapli_netconf

from evpn_data_class import evpn_data
from scrapli_netconf.driver import NetconfScrape


def create_evpn_via_scrapi_netconf(evpn_data, datastore='running'):
    my_device = {
        "host": "192.168.99.91",
        "auth_username": "apiuser",
        "auth_password": "apipassword",
        "auth_strict_key": False,        
    }

    with NetconfScrape(**my_device) as conn:
        response = conn.edit_config(config=evpn_data, target=datastore)
        return response


evpn10 = evpn_data(333, 10333, '10.3.3.3/24', mtu=9000, mgroup='230.1.1.3')
evpn20 = evpn_data(444, 10444, '10.4.4.4/24', mgroup='230.1.1.4', description='2nd anycast SVI (by netconf)', supARP=True)

resp1 = create_evpn_via_scrapi_netconf(evpn10.get_rpc())
resp2 = create_evpn_via_scrapi_netconf(evpn20.get_rpc())

print(f"{resp1.result = }")
print(f"{resp2.result = }")
