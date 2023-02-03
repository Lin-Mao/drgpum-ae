#/bin/bash

export AE_ROOT=/root
export PATTERN_DETECT=$AE_ROOT/scripts/python/show_liveness_pattern.py
export PROFILE_LOG=$AE_ROOT/results/tmp/profile_log

apps=(
darknet
# laghos
miniMDock
XSBench
Huffman
Dwt2d
2MM
3MM
GRAMSCHM
BICG
Pytorch
simpleMultiCopy
)


echo "-------- darknet --------"
python $PATTERN_DETECT -p $PROFILE_LOG/darknet
echo "-------- miniMDock --------"
python $PATTERN_DETECT -p $PROFILE_LOG/miniMDock
echo "-------- XSBench --------"
python $PATTERN_DETECT -p $PROFILE_LOG/XSBench
echo "-------- Huffman --------"
python $PATTERN_DETECT -p $PROFILE_LOG/Huffman
echo "-------- Dwt2d --------"
python $PATTERN_DETECT -p $PROFILE_LOG/Dwt2d
echo "-------- 2MM --------"
python $PATTERN_DETECT -p $PROFILE_LOG/2MM
echo "-------- 3MM --------"
python $PATTERN_DETECT -p $PROFILE_LOG/3MM
echo "-------- GRAMSCHM --------"
python $PATTERN_DETECT -p $PROFILE_LOG/GRAMSCHM
echo "-------- BICG --------"
python $PATTERN_DETECT -p $PROFILE_LOG/BICG
echo "-------- Pytorch --------"
python $PATTERN_DETECT -p $PROFILE_LOG/Pytorch
echo "-------- simpleMultiCopy --------"
python $PATTERN_DETECT -p $PROFILE_LOG/simpleMultiCopy

