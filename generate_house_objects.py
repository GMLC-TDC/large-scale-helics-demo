import sys
import socket


""""
generates the glm files needed for the gridlab-d federate
input params: root_broker, num_houses, houses_per_node
glm files will be added to config_files/hostname directory
"""


def write_glm(start, end, glm_file, hostname):

    with open(glm_file, 'w+') as f:
        f.write("module connection;\n")
        helics_msg_object = f"""object helics_msg{{
     name gridlabd_fed_{hostname};
     configure gridlabd_config_{hostname}.txt;
}}
"""     
        f.write(helics_msg_object)
        f.write("module residential {implicit_enduses NONE;}\n")
        for n in range(int(start), int(end)+1):
            house_object = f"""object house {{
    name house_{n};
    cooling_setpoint random.normal(70, 10);
}};
"""
           
            f.write(house_object)


    

if __name__=="__main__":  
    hostname = socket.gethostname()
    root_broker = sys.argv[1]   
    num_houses = int(sys.argv[2])
    houses_per_node = int(sys.argv[3])
    self_address = socket.gethostbyname(hostname)
    start = 0
    if not hostname == root_broker:
        start = start + houses_per_node
    
    write_glm(start, start+(houses_per_node-1), f"config_files/{hostname}/demo_houses_{start}.glm", hostname)
