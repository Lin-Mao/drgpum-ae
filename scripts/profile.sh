#!/bin/bash

export AE_ROOT=/root
export APPS_DIR=$AE_ROOT/apps

profile_log=$AE_ROOT/results/tmp/profile_log
mkdir -p $profile_log
profile_result=$AE_ROOT/results/memory_reduction.txt
verbose=$AE_ROOT/results/tmp/memory_peak_log.txt

export DRGPUM_PATH=$AE_ROOT/DrGPUM/gvprof
export PATH=${DRGPUM_PATH}/bin:$PATH
export PATH=${DRGPUM_PATH}/hpctoolkit/bin:$PATH
export PATH=${DRGPUM_PATH}/redshow/bin:$PATH

export PATH=/root/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/root/openmpi/lib:$LD_LIBRARY_PATH

# profiling mode
control_knobs="-ck HPCRUN_SANITIZER_LIVENESS_ONGPU=1"

redshow_mode=memory_liveness

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
    esac
done

################################################################################################
#################################### Profile Darknet ###########################################
################################################################################################
echo "--------------------------- Darknet analyzing ----------------------------"
run_darknet="./darknet detector test ./cfg/coco.data ./cfg/yolov4.cfg ./yolov4.weights \
data/dog.jpg -i 0 -thresh 0.25"
version=ori
cd $APPS_DIR
cd darknet_$version
gvprof -v -e $redshow_mode $control_knobs $run_darknet &> /dev/null
echo -n "Darknet $version " > $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/darknet

version=opt
cd $APPS_DIR
cd darknet_$version
gvprof -v -e $redshow_mode $control_knobs $run_darknet &> /dev/null
echo -n "Darknet $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

################################################################################################
##################################### Profile Laghos ###########################################
################################################################################################
############################### MPI can not run in sudo(docker)#################################
# echo "--------------------------- Laghos analyzing -----------------------------"
# run_laghos="./laghos -p 0 -dim 2 -rs 3 -tf 0.75 -pa -d cuda"
# version=ori
# cd $APPS_DIR
# cd laghos_$version/Laghos
# gvprof -v -e $redshow_mode -l "mpirun -np 1" $control_knobs $run_laghos &> /dev/null
# echo -n "Laghos $version " >> $verbose
# cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
# cp -r gvprof-measurements/memory_liveness/ $profile_log/laghos

# version=opt
# cd $APPS_DIR
# cd laghos_$version/Laghos
# gvprof -v -e $redshow_mode -l "mpirun -np 1" $control_knobs $run_laghos &> /dev/null
# echo -n "Laghos $version " >> $verbose
# cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

################################################################################################
#################################### Profile miniMDock #########################################
################################################################################################
echo "--------------------------- miniMDock analyzing --------------------------"
run_minimdock="./bin/autodock_gpu_64wi -lfile ./input/7cpa/7cpa_ligand.pdbqt"
version=ori
cd $APPS_DIR
cd miniMDock_$version
gvprof -v -e $redshow_mode $control_knobs $run_minimdock &> /dev/null
echo -n "miniMDock $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/miniMDock

version=opt
cd $APPS_DIR
cd miniMDock_$version
gvprof -v -e $redshow_mode $control_knobs $run_minimdock &> /dev/null
echo -n "miniMDock $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

################################################################################################
##################################### Profile XSBench ##########################################
################################################################################################
version=ori
cd $APPS_DIR
echo "--------------------------- XSBench analyzing ----------------------------"
run_xsbench="./XSBench -m event -s small -g 100 -l 1700 -h 100"
version=ori
cd XSBench_$version/cuda

gvprof -v -e $redshow_mode $control_knobs $run_xsbench &> /dev/null
echo -n "XSBench $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/XSBench

version=opt
cd $APPS_DIR
cd XSBench_$version/cuda
gvprof -v -e $redshow_mode $control_knobs $run_xsbench &> /dev/null
echo -n "XSBench $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

################################################################################################
##################################### Profile Rodinia ##########################################
################################################################################################

######################################## huffman ###############################################
version=ori
cd $APPS_DIR && cd rodinia_$version
echo "--------------------------- huffman analyzing ----------------------------"
run_huffman="./pavle ../data/huffman/test1024_H2.206587175259.in"
cd huffman
gvprof -v -e $redshow_mode $control_knobs $run_huffman &> /dev/null
echo -n "Huffman $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/Huffman

version=opt
cd $APPS_DIR && cd rodinia_$version
cd huffman
gvprof -v -e $redshow_mode $control_knobs $run_huffman &> /dev/null
echo -n "Huffman $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
########################################## dwt2d ###############################################
version=ori
cd $APPS_DIR && cd rodinia_$version
cd dwt2d
echo "--------------------------- dwt2d analyzing ------------------------------"
run_dwt2d="./dwt2d 192.bmp -d 192x192 -f -5 -l 3"
gvprof -v -e $redshow_mode $control_knobs $run_dwt2d &> /dev/null
echo -n "Dwt2d $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/Dwt2d

version=opt
cd $APPS_DIR && cd rodinia_$version
cd dwt2d
gvprof -v -e $redshow_mode $control_knobs $run_dwt2d &> /dev/null
echo -n "Dwt2d $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

################################################################################################
#################################### Profile Polybench #########################################
################################################################################################

########################################## 2MM #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "--------------------------- 2MM analyzing --------------------------------"
run_2mm="./2mm.exe"
cd 2MM
gvprof -v -e $redshow_mode $control_knobs $run_2mm &> /dev/null
echo -n "2MM $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/2MM

version=opt
cd $APPS_DIR && cd polybench_$version
cd 2MM
gvprof -v -e $redshow_mode $control_knobs $run_2mm &> /dev/null
echo -n "2MM $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

########################################## 3MM #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "--------------------------- 3MM analyzing --------------------------------"
run_3mm="./3mm.exe"
cd 3MM
gvprof -v -e $redshow_mode $control_knobs $run_3mm &> /dev/null
echo -n "3MM $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/3MM

version=opt
cd $APPS_DIR && cd polybench_$version
cd 3MM
gvprof -v -e $redshow_mode $control_knobs $run_3mm &> /dev/null
echo -n "3MM $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

######################################## GRAMSCHM ###############################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "--------------------------- GRAMSCHM analyzing ---------------------------"
run_gramschm="./gramschmidt.exe"
cd GRAMSCHM
gvprof -v -e $redshow_mode $control_knobs $run_gramschm &> /dev/null
echo -n "GRAMSCHM $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/GRAMSCHM

version=opt
cd $APPS_DIR && cd polybench_$version
cd GRAMSCHM
gvprof -v -e $redshow_mode $control_knobs $run_gramschm &> /dev/null
echo -n "GRAMSCHM $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose


########################################## BICG #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "--------------------------- BICG analyzing -------------------------------"
run_bicg="./bicg.exe"
cd BICG
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null
# echo -n "BICG $version " >> $verbose
# cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/BICG

version=opt
cd $APPS_DIR && cd polybench_$version
cd BICG
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null
# echo -n "BICG $version " >> $verbose
# cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose

################################################################################################
#################################### Profile Pytorch ###########################################
################################################################################################
version=ori
cd $APPS_DIR
echo "---------------------------- Pytorch analyzing ---------------------------"
eval "$($AE_ROOT/anaconda3/bin/conda shell.bash hook)"
conda activate torch
run_pytorch="python resnet50-conv-unit.py"
cd pytorch_$version
hpcrun -e gpu=nvidia $run_pytorch &> /dev/null
rm hpctoolkit-python-measurements/*hpcrun
hpcrun -e gpu=nvidia,memory_liveness -ck HPCRUN_SANITIZER_TORCH_ANALYSIS_ONGPU=1 -o hpctoolkit-python-measurements/ $run_pytorch &> /dev/null
conda deactivate
echo -n "Pytorch $version " >> $verbose
cat hpctoolkit-python-measurements/memory_liveness/submemory_info.txt | head -n 3| tail -n -1 >> $verbose
cp -r hpctoolkit-python-measurements/memory_liveness/ $profile_log/Pytorch

version=opt
cd $APPS_DIR
cd pytorch_$version
conda activate torch-$version
hpcrun -e gpu=nvidia $run_pytorch &> /dev/null
rm hpctoolkit-python-measurements/*hpcrun
hpcrun -e gpu=nvidia,memory_liveness -ck HPCRUN_SANITIZER_TORCH_ANALYSIS_ONGPU=1 -o hpctoolkit-python-measurements/ $run_pytorch &> /dev/null
conda deactivate
echo -n "Pytorch $version " >> $verbose
cat hpctoolkit-python-measurements/memory_liveness/submemory_info.txt | head -n 3| tail -n -1 >> $verbose

################################################################################################
################################# Profile simpleMultiCopy ######################################
################################################################################################
version=ori
cd $APPS_DIR && cd simpleMultiCopy_$version && cd Samples/0_Introduction/simpleMultiCopy
echo "----------------------- simpleMultiCopy analyzing ------------------------"
run_simpleMultiCopy="./simpleMultiCopy"
gvprof -v -e $redshow_mode $control_knobs $run_simpleMultiCopy &> /dev/null
echo -n "simpleMultiCopy $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
cp -r gvprof-measurements/memory_liveness/ $profile_log/simpleMultiCopy

version=opt
cd $APPS_DIR && cd simpleMultiCopy_$version && cd Samples/0_Introduction/simpleMultiCopy
gvprof -v -e $redshow_mode $control_knobs $run_simpleMultiCopy &> /dev/null
echo -n "simpleMultiCopy $version " >> $verbose
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1 >> $verbose
