import sys
import socket


""""
generates the glm files needed for the gridlab-d federate
input params: root_broker, num_houses, houses_per_node
glm files will be added to config_files/hostname directory
"""


def write_glm(start, end, glm_file, hostname):

    with open(glm_file, 'w+') as f:
        clock = f"""clock {{
    timezone PST8;
    starttime '2002-01-01 00:00:00';
    stoptime '2002-01-01 08:00:00';
}}
"""
        f.write(clock)
        f.write("#define stylesheet=http://gridlab-d.svn.sourceforge.net/viewvc/gridlab-d/trunk/core/gridlabd-2_0;\n")
        f.write("#set minimum_timestep=60.000000;\n")
        f.write("#set profiler=1;\n")
        f.write("#set relax_naming_rules=1;\n")
        f.write("module tape {\n}\n")
        f.write("module connection;\n")

        helics_msg_object = f"""object helics_msg{{
     name gridlabd_fed_{hostname};
     configure config_files/{hostname}/gridlabd_fed_{hostname}.json;
}}
"""     
        f.write(helics_msg_object)
        f.write("module climate {\n}\n")
        f.write("module residential {implicit_enduses NONE;}\n")

        climate_object = f"""object climate {{
    name ClimateWeather;
    tmyfile include/AZ-Phoenix.tmy3;
    interpolate QUADRATIC;
}};
""" 
        f.write(climate_object)
        
        for n in range(int(start), int(end)+1):
            house_object = f"""object house {{
    name house_{n};
    cooling_setpoint random.normal(70, 10);
    total_load 0;
}};
"""
           
            f.write(house_object)
    
        collector_object = f"""object collector {{
        name TotalLoadCollector;
        group class=house;
        interval 900;
        property sum(total_load);
}};
"""
        f.write(collector_object)

    

if __name__=="__main__":  
    hostname = socket.gethostname()
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    self_address = socket.gethostbyname(hostname)
    
    write_glm(start, end, f"config_files/{hostname}/demo_houses_{start}.glm", hostname)
