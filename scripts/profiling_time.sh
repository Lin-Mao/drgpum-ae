#!/bin/bash

# profiling mode
control_knobs=""

# result folder
export AE_ROOT=/root
export APPS_DIR=$AE_ROOT/apps
export app_path=$APPS_DIR

export DRGPUM_PATH=$AE_ROOT/DrGPUM/gvprof
export PATH=${DRGPUM_PATH}/bin:$PATH
export PATH=${DRGPUM_PATH}/hpctoolkit/bin:$PATH
export PATH=${DRGPUM_PATH}/redshow/bin:$PATH

export PATH=/root/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/root/openmpi/lib:$LD_LIBRARY_PATH
# profiling version ori or opt
version=ori
# interations for each profiling
iteration=10
# (seconds) interval between each profiling
interval=5

while test "x$1" != x
do
    arg="$1"; shift
    case "$arg" in
        -e)
            redshow_mode=$1
            shift
            ;;
        -ck)
            control_knobs=$1
            shift
            ;;
        -i)
            interval=$1
            shift
            ;;
        -n)
            iteration=$1
            shift
            ;;
    esac
done

if [ -z "$redshow_mode" ]
then
    echo "Empty mode. Please specify profiling mode."
    exit
fi

# run_experiment
cd $AE_ROOT

############################## darknet ##############################
echo "------------------ darknet ------------------"
run_darknet="./darknet detector test ./cfg/coco.data ./cfg/yolov4.cfg ./yolov4.weights \
data/dog.jpg -i 0 -thresh 0.25"

cd $app_path
cd darknet_$version
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_darknet &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_darknet &> /dev/null)
echo ""
done
echo ""


# ############################## laghos ##############################
# echo "------------------ laghos ------------------"
# run_laghos="./laghos -p 0 -dim 2 -rs 3 -tf 0.75 -pa -d cuda"

# cd $app_path
# cd laghos_$version/Laghos
# # warm-up
# gvprof -v -e $redshow_mode -l "mpirun -np 1" $control_knobs $run_laghos &> /dev/null

# for ((i = 0; i < $iteration; i++))
# do
# echo "$((i+1)) round"
# sleep $interval
# time (mpirun -np 1 hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_laghos &> /dev/null)
# echo ""
# done
# echo ""


############################## miniMDock ##############################
echo "------------------ miniMDock ------------------"
run_minimdock="./bin/autodock_gpu_64wi -lfile ./input/7cpa/7cpa_ligand.pdbqt"

cd $app_path
cd miniMDock_$version
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_minimdock &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_minimdock &> /dev/null)
echo ""
done
echo ""


############################## XSBench ##############################
echo "------------------ XSBench ------------------"
run_xsbench="./XSBench -m event -s small -g 100 -l 1700 -h 100"

cd $app_path
cd XSBench_$version/cuda
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_xsbench &> /dev/null
 
for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_xsbench &> /dev/null)
echo ""
done
echo ""


############################## Rodinia ##############################
cd $app_path
cd rodinia_$version

############################## huffman ##############################
echo "------------------ huffman ------------------"
run_huffman="./pavle ../data/huffman/test1024_H2.206587175259.in"

cd huffman
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_huffman &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_huffman &> /dev/null)
echo ""
done
echo ""

############################## dwt2d ##############################
echo "------------------ dwt2d ------------------"
run_dwt2d="./dwt2d 192.bmp -d 192x192 -f -5 -l 3"

cd ../dwt2d/
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_dwt2d &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_dwt2d &> /dev/null)
echo ""
done
echo ""

############################## Polybench ##############################
cd $app_path
cd polybench_$version

############################## 2MM ##############################
echo "------------------ 2MM ------------------"
run_2mm="./2mm.exe"
cd 2MM
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_2mm &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_2mm &> /dev/null)
echo ""
done
echo ""

############################## 3MM ##############################
echo "------------------ 3MM ------------------"
run_3mm="./3mm.exe"
cd ../3MM
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_3mm &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_3mm &> /dev/null)
echo ""
done
echo ""

############################## GRAMSCHM ##############################
echo "------------------ GRAMSCHM ------------------"
run_gramschm="./gramschmidt.exe"
cd ../GRAMSCHM
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_gramschm &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_gramschm &> /dev/null)
echo ""
done
echo ""

############################## BICG ##############################
echo "------------------ BICG ------------------"
run_bicg="./bicg.exe"
cd ../BICG
# warm-up
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs $run_bicg &> /dev/null)
echo ""
done
echo ""

############################## Pytorch ##############################
eval "$($AE_ROOT/anaconda3/bin/conda shell.bash hook)"
conda activate torch
echo "------------------ Pytorch ------------------"
run_pytorch="python resnet50-conv-unit.py"
cd $app_path
cd pytorch_$version
# warm-up
hpcrun -e gpu=nvidia $run_pytorch &> /dev/null
rm hpctoolkit-python-measurements/*hpcrun
hpcrun -e gpu=nvidia,$redshow_mode $control_knobs -o hpctoolkit-python-measurements/ $run_pytorch &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time (hpcrun -e gpu=nvidia,$redshow_mode $control_knobs -o hpctoolkit-python-measurements/ $run_pytorch &> /dev/null)
echo ""
done
echo ""
conda deactivate

############################## simpleMultiCopy ##############################
echo "------------------ simpleMultiCopy ------------------"
run_simpleMultiCopy="./simpleMultiCopy"
cd $app_path
cd simpleMultiCopy_$version
cd Samples/0_Introduction/simpleMultiCopy
# warm-up
$run_simpleMultiCopy &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time (gvprof -v -e $redshow_mode $control_knobs $run_simpleMultiCopy &> /dev/null)
echo ""
done
echo ""
echo "------------------ END ------------------"