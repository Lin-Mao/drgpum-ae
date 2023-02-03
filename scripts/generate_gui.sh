#!/bin/bash
export AE_ROOT=/root
export RESULTS_PATH=$AE_ROOT/results
export SCRIPTS_PATH=$AE_ROOT/scripts
export PROFILE_LOG=$AE_ROOT/results/tmp/profile_log

python $SCRIPTS_PATH/python/generate_gui.py -p $PROFILE_LOG/simpleMultiCopy -o $RESULTS_PATH
echo "---------------------------------- done ----------------------------------"