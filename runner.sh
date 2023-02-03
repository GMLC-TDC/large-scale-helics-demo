#!/bin/bash


# Args: main hostname, main node adddress, start fed, end fed, total houses, houses/node


main_host_name=$1
main_address=$2
start_fed=$3
end_fed=$4
total_houses=$5
houses_per_node=$6

my_hostname=$(hostname)
my_address=$(hostname -i)


echo "
hostname: $my_hostname
main address: $main_address
address: $my_address
total houses: $total_houses
houses per node: $houses_per_node
start: $start_fed
end: $end_fed
"

mkdir -p "config_files/${my_hostname}"

python3 write_config_files.py "${main_host_name}" "${houses_per_node}"
python3 generate_house_objects.py "${start_fed}" "${end_fed}"

echo "creating broker at ${my_hostname} : ${my_address}"
num_feds_sub=$((houses_per_node+1))                 # add gridlabd federate
num_feds_main=$((houses_per_node+2))                # add both central controller and gridlabd federates
if [[ "${main_host_name}" == "${my_hostname}" ]]; then
    helics_broker -f "${num_feds_main}" --coretype "zmqss" --name "mainbroker" --broker_address "tcp://${main_address}" --root &
else 
    helics_broker -f "${num_feds_sub}" --coretype "zmqss" --name "subbroker_${my_hostname}" --broker_address "tcp://${main_address}" &
fi


sleep 10
python3 HELICS_demo.py "${main_host_name}" "${start_fed}" "${end_fed}" & gridlabd "config_files/${my_hostname}/demo_houses_${start_fed}.glm"

wait