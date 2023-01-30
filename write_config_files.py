import json
import socket
import sys

""""
generates the config files needed for the gridlab-d federate
uses config_files/config_temaplte.txt as a template
config files will be added to config_files/hostname directory
"""

def write_config(main_host, host_name, houses_per_node):  
    if main_host == host_name:
        broker_name="mainbroker"
    else: broker_name=f"subbroker{host_name}"
    broker_address = socket.gethostbyname(host_name)
    with open("config_files/config_template.txt", "r+") as f:
        f.seek(0)
        template = json.load(f)
        template["name"] = f"gridlabd_fed_{host_name}"
        template["broker_address"]=broker_address
        template["broker"] = "mainbroker"
        template["core_name"] = "gridlabd"
        template["core_init_string"] = f"--federates={houses_per_node} --broker={broker_name}"
        template["publications"][0]["info"] = "{\"object\" : \"house\", \"property\" : \"total_load\"}"
        template["endpoints"][0]["name"] = f"gridlabd_{host_name}"
    with open(f"config_files/{host_name}/gridlabd_config_{host_name}.txt", "w+") as f2:
        f2.write(json.dumps(template, ensure_ascii=False, indent=4))

if __name__=="__main__":  
    main_host = sys.argv[1]
    houses_per_node = sys.argv[2]
    host_name = socket.gethostname()
    print(f"writing config files for {host_name}")
    write_config(main_host, host_name, houses_per_node)