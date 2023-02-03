#/bin/bash
export SCRIPTS_PATH=$AE_ROOT/scripts
export RESULTS_PATH=$AE_ROOT/results

python $SCRIPTS_PATH/python/report_peak_reduction.py -p $RESULTS_PATH/tmp