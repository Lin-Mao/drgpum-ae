#/bin/bash

export AE_ROOT=/root
export SCRIPTS_PATH=$AE_ROOT/scripts
export RESULTS_PATH=$AE_ROOT/results

echo "##########################################################################"
echo "##         Program   start  at  $(date)            ##"
echo "##         Estimated to end at  $(date -d "+1 hour")            ##"
echo "##                  May vary from machine to machine.                   ##"
echo "##########################################################################"

echo "------------------------------ profiling ---------------------------------"
bash $SCRIPTS_PATH/profile.sh

echo "--------------------------- analyzing patterns ---------------------------"
bash $SCRIPTS_PATH/pattern_detect.sh > $RESULTS_PATH/pattens.txt

echo "-------------------- reporting memory preak reduction --------------------"
bash $SCRIPTS_PATH/report_peak_reduction.sh > $RESULTS_PATH/memory_peak.txt

echo "--------------------------- analyzing speedup ----------------------------"
bash $SCRIPTS_PATH/speedup.sh &> $RESULTS_PATH/tmp/speedup_time.log
python $SCRIPTS_PATH/python/show_elapsed_speedup_time.py $RESULTS_PATH/tmp/speedup_time.log >> $RESULTS_PATH/memory_peak.txt

echo "---------------------------------- done ----------------------------------"
