#!/bin/bash

export AE_ROOT=/root
export APPS_DIR=$AE_ROOT/apps
export RESULTS_PATH=$AE_ROOT/results
export SCRIPTS_PATH=$AE_ROOT/scripts

# interations for each profiling
iter=10
# (seconds) interval between each profiling
interval=5

cd $AE_ROOT

echo "##########################################################################"
echo "##         Program   start  at  $(date)         ##"
echo "##         Estimated to end at  $(date -d "+4 hour")         ##"
echo "##                  May vary from machine to machine.                   ##"
echo "##########################################################################"

# execution
echo "-------------------------- original executing ----------------------------"
bash $SCRIPTS_PATH/execution_time.sh &> $RESULTS_PATH/tmp/execution_profile.log

# object-level analysis

bash $SCRIPTS_PATH/profiling_time.sh -e memory_liveness -ck "-ck HPCRUN_SANITIZER_LIVENESS_ONGPU=1" -i $interval -n $iter &> $RESULTS_PATH/tmp/object_level.log

# set whitelist
echo "------------------------- object-level analyzing -------------------------"
python $SCRIPTS_PATH/python/set_whitelist.py $APPS_DIR &> /dev/null

# intra-object-level analysis
echo "---------------------- intra-object-level analyzing ----------------------"
bash $SCRIPTS_PATH/profiling_time.sh -e memory_heatmap -ck "-ck HPCRUN_SANITIZER_KERNEL_SAMPLING_FREQUENCY=100 -ck HPCRUN_SANITIZER_WHITELIST=whitelist" -i $interval -n $iter &> $RESULTS_PATH/tmp/intra_object.log

echo "-------------------------- overhead analyzing ----------------------------"
time_path=$RESULTS_PATH/tmp/time
mkdir -p $time_path

python $SCRIPTS_PATH/python/show_elapsed_time.py $RESULTS_PATH/tmp/execution_profile.log > $time_path/baseline.log

python $SCRIPTS_PATH/python/show_elapsed_time.py $RESULTS_PATH/tmp/object_level.log > $time_path/object_level.log

python $SCRIPTS_PATH/python/show_elapsed_time.py $RESULTS_PATH/tmp/intra_object.log > $time_path/intra_object.log


eval "$($AE_ROOT/anaconda3/bin/conda shell.bash hook)"
conda create -n overhead python=3.8 -y &> /dev/null
conda activate overhead
conda install matplotlib numpy -y &> /dev/null
python $SCRIPTS_PATH/python/overhead.py -p $time_path/ -o $RESULTS_PATH/ &> /dev/null
conda deactivate
echo "---------------------------------- done ----------------------------------"