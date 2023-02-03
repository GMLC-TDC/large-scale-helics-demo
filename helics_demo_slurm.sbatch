#!/bin/bash

#SBATCH --ntasks-per-node=1
#SBATCH -N 10
#SBATCH -n 10
#SBATCH -p pbatch
#SBATCH -t 08:00:00

###### Potential configs that may be needed #######
PATH=$PATH:~/.local/bin
PATH=$PATH:~/HELICS_demo/gridlab-d/bin
module load python/3.8.2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
if [ -n "$SLURM_JOB_ID" ]; then
    sbatch_orig_file="$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')"
    SCRIPT_DIR="$(cd "$(dirname "${sbatch_orig_file}")" >/dev/null 2>&1 && pwd)"
fi
echo "sbatch script location: $SCRIPT_DIR"

if [[ "${CORE_TYPE}" == "" ]]; then
    CORE_TYPE="zmqss"
fi

if [[ "${HOUSES_PER_NODE}" == "" ]]; then
    HOUSES_PER_NODE=50
fi

echo "Running HELICS demo: ${HOUSES_PER_NODE} houses/${SLURM_JOB_NUM_NODES} nodes, with core type ${CORE_TYPE}"

output_folder="DemoResults-${CORE_TYPE}-N${SLURM_JOB_NUM_NODES}-job-${SLURM_JOB_ID}"
mkdir -p "${output_folder}"


echo "
CLUSTER: ${SLURM_CLUSTER_NAME}
NUM NODES: ${SLURM_JOB_NUM_NODES}
HOUSES PER NODE: ${HOUSES_PER_NODE}
SLURM_SUBMIT_HOST = ${SLURM_SUBMIT_HOST}
SLURMD_NODENAME = ${SLURMD_NODENAME}
"
main_address=$(hostname -i)
echo "main address: ${main_address}"
TOTAL_HOUSES=$((SLURM_JOB_NUM_NODES * HOUSES_PER_NODE))
total_nodes=$((TOTAL_HOUSES + 2))


for i in $(seq 1 "${SLURM_JOB_NUM_NODES}"); do
    ((idx = ${i} - 1))
    ((start = ${idx}*${HOUSES_PER_NODE}))
    ((end = ${start} + ${HOUSES_PER_NODE} -1))
    srun --ntasks 1 --nodes 1 "$SCRIPT_DIR/runner.sh" "${HOSTNAME}" "${main_address}" "${start}" "${end}" "${TOTAL_HOUSES}" "${HOUSES_PER_NODE}" &
done

wait

echo "Done"