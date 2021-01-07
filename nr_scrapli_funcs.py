from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions.print_result import print_result
from nornir_scrapli.tasks import (
    netconf_capabilities,
    netconf_lock,
    netconf_unlock,
    netconf_edit_config,
    netconf_get,
    netconf_get_config,
    netconf_validate,
    netconf_discard,
    netconf_commit,
    netconf_rpc    
)

init_datastore_rpc = """<copy-config>
    <target>
      <{target}/>
    </target>
    <source>
      <running/>
    </source>
  </copy-config>"""


def nr_netconf_edit(config: str, site: str) -> bool:
    ret = False
    nr = InitNornir(config_file="nornir_data/config.yaml")
    nr = nr.filter(site=site)

    host = nr.inventory.hosts
    print(f"host = {host}")


    def deploy_and_verify(task: Task, config: str, target='candidate') -> Result:      
        name = f"initialize a datastore: {target}"        
        task.run(name=name, task=netconf_rpc, 
                filter_=init_datastore_rpc.format(target=target))
        
        task.run(name="discard changes so the datastore can be locked",              
                task=netconf_discard)
        
        task.run(name="lock the datastore",                
                task=netconf_lock, 
                target=target)
        
        task.run(name="change config in the datastore",                
                task=netconf_edit_config,
                config=config, 
                target=target)
        
        task.run(name="validate config",                
                task=netconf_validate,            
                source=target)
        
        return Result(
            host=task.host,
            result=f"{task.host}: config applied and verified",
        )
   
    res_deploy = nr.run(name="deploy and verify config",                
                task=deploy_and_verify,
                config=config)
    print_result(res_deploy)

    if res_deploy.failed:
        print(f"config deployment (lock/edit/verify) has failed on {res_deploy.failed_hosts}")
        res_discard = nr.run(name="rollback changes on all hosts",                            
                            task=netconf_discard)      

        if res_discard.failed:
            print(f"couldn't discard changes on {res_discard.failed_hosts}\ncli monkey needed")
    else:
        res_commit = nr.run(name="commit",                            
                            task=netconf_commit)      
        print_result(res_commit)

        if res_commit.failed:
            print(f"commit failed on {res_commit.failed_hosts}\ncli monkey needed")
        else:
            print("changes were applied successfully!")
            ret = True

    res_unlock = nr.run(name="unlock datastores",                        
                        task=netconf_unlock, target='candidate')
    
    if res_unlock.failed:
        print(f"unlock failed on host: {res_unlock.failed_hosts}")

    return ret


def nr_netconf_get(filter_: str, site: str) -> bool:

    nr = InitNornir(config_file="nornir_data/config.yaml")
    nr = nr.filter(site=site)

    hosts = nr.inventory.hosts
    print(f"hosts = {hosts}")

    res_get_config = nr.run(name="get config",                
                task=netconf_get,
                filter_=filter_)
    #print_result(res_get_config)

    from evpn_xml_parse import get_evpn_data_from_xml
    res = {}
    for host in hosts:
        host_result = res_get_config[host][0].result
        data = get_evpn_data_from_xml(host_result)
        res[host] = data

    return res
