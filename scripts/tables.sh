#/bin/bash

export AE_ROOT=/root
export SCRIPTS_PATH=$AE_ROOT/scripts
export RESULTS_PATH=$AE_ROOT/results

bash $SCRIPTS_PATH/profile.sh
bash $SCRIPTS_PATH/pattern_detect.sh > $RESULTS_PATH/pattens.txt
bash $SCRIPTS_PATH/report_peak_reduction.sh > $RESULTS_PATH/pattens.txt

