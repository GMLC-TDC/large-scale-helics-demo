import json
import socket
import sys

""""
generates the config files needed for the gridlab-d federate
uses config_files/config_temaplte.txt as a template
config files will be added to config_files/hostname directory
"""

def write_config(main_host, host_name, houses_per_node):
    broker_address = "tcp://"+str(socket.gethostbyname(host_name))
    template = {}
    template["name"] = f"gridlabd_fed_{host_name}"
    template["coreType"] = "zmqss"
    template["coreName"] = f"gridlabd_{host_name}"
    template["coreInit"] = f"--federates={houses_per_node} --broker={broker_address}"
    template["publications"] = []
    publication_attributes={}
    template["publications"].append(publication_attributes)
    template["publications"][0]["key"]="centralcontroller/gridlabd"
    template["publications"][0]["global"]=False
    template["publications"][0]["type"]="double"
    template["publications"][0]["unit"]="VA"
    template["publications"][0]["info"] = {"object" : "TotalLoadCollector", "property" : "sum(total_load)"}

    template["endpoints"]=[]
    endpoint_attributes={}
    template["endpoints"].append(endpoint_attributes)
    template["endpoints"][0]["key"] = f"gridlabd_{host_name}"
    template["endpoints"][0]["global"] = False
    template["endpoints"][0]["type"] = "double"
    template["endpoints"][0]["info"] = {"message_type": "JSON", "receive_messages":True}

    with open(f"config_files/{host_name}/gridlabd_fed_{host_name}.json", "w+") as f2:
        f2.write(json.dumps(template, ensure_ascii=False, indent=4))
    



if __name__=="__main__":  
    main_host = sys.argv[1]
    houses_per_node = sys.argv[2]
    host_name = socket.gethostname()
    print(f"writing config files for {host_name}")
    write_config(main_host, host_name, houses_per_node)