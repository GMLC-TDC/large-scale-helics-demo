#!/bin/bash


# Args: main hostname, start fed, end fed, total houses, houses/node
# Passthrough at end of arg handling: broker, coretype, msg_size, msg_count, max_index (update max_index script to multiply SLURM_JOB_NUM_NODES by feds per node)


host_name=$1
shift

start_fed=$1
shift

end_fed=$1
shift

total_houses=$1
shift

houses_per_node=$1
shift

my_hostname=$(bash -c "echo \$(hostname)")
my_address=$(bash -c "echo \$(hostname -I)")

echo "
hostname: $my_hostname
address: $my_address
total houses: $total_houses
houses per node: $houses_per_node
start: $start_fed
end: $end_fed
"

mkdir -p "config_files/${my_hostname}"

python3 write_config_files.py "${host_name}" "${houses_per_node}"
python3 generate_house_objects.py "${host_name}" "${total_houses}" "${houses_per_node}"

num_feds=$(( total_house * houses_per_node))
if [[ "${host_name}" == "${my_hostname}" ]]; then
    echo "creating mainbroker"
    helics_broker --all -f "${num_feds}" --coretype "zmqss" --name "mainbroker" --broker_address "${host_name}" --root &
else 
    echo "creating subbroker${my_hostname}"
    helics_broker --all -f "${num_feds}" --coretype "zmqss" --name "subbroker${my_hostname}" --broker_address "${host_name}" &
fi


sleep 5
python3 HELICS_demo.py "${host_name}" "${start_fed}" "${end_fed}" & gridlabd "config_files/${my_hostname}/demo_houses_${start_fed}.glm"

wait