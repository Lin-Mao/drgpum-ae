#!/bin/bash

# result folder
export AE_ROOT=/root
export APPS_DIR=$AE_ROOT/apps
export app_path=$APPS_DIR
# profiling version ori or opt
version=ori
# interations for each profiling
iteration=10
# (seconds) interval between each profiling
interval=5

while test "x$1" != x
do
    arg="$1" ; shift
    case "$arg" in
        -v)
            version=$1
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

# run_experiment
cd $AE_ROOT

############################## darknet ##############################
echo "------------------ darknet ------------------"
run_darknet="./darknet detector test ./cfg/coco.data ./cfg/yolov4.cfg ./yolov4.weights \
data/dog.jpg -i 0 -thresh 0.25"

cd $app_path
cd darknet_$version
# warm-up
$run_darknet &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_darknet &> /dev/null)
echo ""
done
echo ""


# ############################## laghos ##############################
# echo "------------------ laghos ------------------"
# run_laghos="./laghos -p 0 -dim 2 -rs 3 -tf 0.75 -pa -d cuda"

# cd $app_path
# cd laghos_$version/Laghos
# # warm-up
# $run_laghos &> /dev/null

# for ((i = 0; i < $iteration; i++))
# do
# echo "$((i+1)) round execution"
# sleep $interval
# time ($run_laghos &> /dev/null)
# echo ""
# done
# echo ""


############################## miniMDock ##############################
echo "------------------ miniMDock ------------------"
run_minimdock="./bin/autodock_gpu_64wi -lfile ./input/7cpa/7cpa_ligand.pdbqt"

cd $app_path
cd miniMDock_$version
# warm-up
$run_minimdock &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_minimdock &> /dev/null)
echo ""
done
echo ""


############################## XSBench ##############################
echo "------------------ XSBench ------------------"
run_xsbench="./XSBench -m event -s small -g 100 -l 1700 -h 100"

cd $app_path
cd XSBench_$version/cuda
# warm-up
$run_xsbench &> /dev/null
 
for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_xsbench &> /dev/null)
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
$run_huffman &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_huffman &> /dev/null)
echo ""
done
echo ""

############################## dwt2d ##############################
echo "------------------ dwt2d ------------------"
run_dwt2d="./dwt2d 192.bmp -d 192x192 -f -5 -l 3"

cd ../dwt2d/
# warm-up
$run_dwt2d &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_dwt2d &> /dev/null)
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
$run_2mm &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_2mm &> /dev/null)
echo ""
done
echo ""

############################## 3MM ##############################
echo "------------------ 3MM ------------------"
run_3mm="./3mm.exe"
cd ../3MM
# warm-up
$run_3mm &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_3mm &> /dev/null)
echo ""
done
echo ""

############################## GRAMSCHM ##############################
echo "------------------ GRAMSCHM ------------------"
run_gramschm="./gramschmidt.exe"
cd ../GRAMSCHM
# warm-up
$run_gramschm &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_gramschm &> /dev/null)
echo ""
done
echo ""

############################## BICG ##############################
echo "------------------ BICG ------------------"
run_bicg="./bicg.exe"
cd ../BICG
# warm-up
$run_bicg &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_bicg &> /dev/null)
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
$run_pytorch &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round execution"
sleep $interval
time ($run_pytorch &> /dev/null)
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
time ($run_simpleMultiCopy &> /dev/null)
echo ""
done
echo ""

echo "------------------ END ------------------"