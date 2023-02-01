#/bin/bash

export AE_ROOT=/root
export PATTERN_DETECT=$AE_ROOT/scripts/show_liveness_pattern.py
export PROFILE_LOG=$AE_ROOT/results/profile_log

apps=(
darknet
miniMDock
Huffman
Dwt2d
2MM
3MM
GRAMSCHM
BICG
Pytorch
simpleMultiCopy
)

for app in "${apps[@]}";
do
    echo "----- Patterns of $app -----"
    python $PATTERN_DETECT -p $PROFILE_LOG/$app
done
