#!/bin/bash

export AE_ROOT=/home/asplos-ae

export DRGPUM_PATH=$AE_ROOT/DrGPUM/gvprof
export PATH=${DRGPUM_PATH}/bin:$PATH
export PATH=${DRGPUM_PATH}/hpctoolkit/bin:$PATH
export PATH=${DRGPUM_PATH}/redshow/bin:$PATH

mkdir -p $AE_ROOT/profile_log
profile_log=$AE_ROOT/profile_log

# A100:80, RTX 3090:86
sm=86
# profiling mode
control_knobs="-ck HPCRUN_SANITIZER_LIVENESS_ONGPU=1"

redshow_mode=memory_liveness

while test "x$1" != x
do
    arg="$1"; shift
    case "$arg" in
        -sm)
            sm=$1
            shift
            ;;
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
echo "------------------ Darknet analyzing ------------------"
run_darknet="./darknet detector test ./cfg/coco.data ./cfg/yolov4.cfg ./yolov4.weights \
data/dog.jpg -i 0 -thresh 0.25"
version=ori
cd $APPS_DIR
cd darknet_$version
gvprof -v -e $redshow_mode $control_knobs $run_darknet &> /dev/null
echo -n "Darknet $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/darknet

version=opt
cd $APPS_DIR
cd darknet_$version
gvprof -v -e $redshow_mode $control_knobs $run_darknet &> /dev/null
echo -n "Darknet $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1

################################################################################################
##################################### Profile Laghos ###########################################
################################################################################################
echo "------------------ Laghos analyzing ------------------"
run_laghos="./laghos -p 0 -dim 2 -rs 3 -tf 0.75 -pa -d cuda"
version=ori
cd $APPS_DIR
cd laghos_$version/Laghos
gvprof -v -e $redshow_mode -l "mpirun -np 1" $control_knobs $run_laghos &> /dev/null
echo -n "Laghos $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/laghos

version=opt
cd $APPS_DIR
cd laghos_$version/Laghos
gvprof -v -e $redshow_mode -l "mpirun -np 1" $control_knobs $run_laghos &> /dev/null
echo -n "Laghos $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1

################################################################################################
#################################### Profile miniMDock #########################################
################################################################################################
echo "------------------ miniMDock analyzing ------------------"
run_minimdock="./bin/autodock_gpu_64wi -lfile ./input/7cpa/7cpa_ligand.pdbqt"
version=ori
cd $APPS_DIR
cd miniMDock_$version
gvprof -v -e $redshow_mode $control_knobs $run_minimdock &> /dev/null
echo -n "miniMDock $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/miniMDock

version=opt
cd $APPS_DIR
cd miniMDock_$version
gvprof -v -e $redshow_mode $control_knobs $run_minimdock &> /dev/null
echo -n "miniMDock $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1

################################################################################################
#################################### Profile Polybench #########################################
################################################################################################

######################################## huffman ###############################################
version=ori
cd $APPS_DIR && cd rodinia_$version
echo "------------------ huffman $redshow_mode ------------------"
run_huffman="./pavle ../data/huffman/test1024_H2.206587175259.in"
cd huffman
gvprof -v -e $redshow_mode $control_knobs $run_huffman &> /dev/null
echo -n "Huffman $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/Huffman

version=opt
cd $APPS_DIR && cd rodinia_$version
cd huffman
gvprof -v -e $redshow_mode $control_knobs $run_huffman &> /dev/null
echo -n "Huffman $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
########################################## dwt2d ###############################################
version=ori
cd $APPS_DIR && cd rodinia_$version
cd dwt2d
echo "------------------ dwt2d $redshow_mode ------------------"
run_dwt2d="./dwt2d 192.bmp -d 192x192 -f -5 -l 3"
gvprof -v -e $redshow_mode $control_knobs $run_dwt2d &> /dev/null
echo -n "Dwt2d $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/Dwt2d

version=opt
cd $APPS_DIR && cd rodinia_$version
cd dwt2d
gvprof -v -e $redshow_mode $control_knobs $run_dwt2d &> /dev/null
echo -n "Dwt2d $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1

################################################################################################
#################################### Profile Polybench #########################################
################################################################################################

########################################## 2MM #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "------------------ 2MM $redshow_mode ------------------"
run_2mm="./2mm.exe"
cd 2MM
gvprof -v -e $redshow_mode $control_knobs $run_2mm &> /dev/null
echo -n "2MM $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/2MM

version=opt
cd $APPS_DIR && cd polybench_$version
cd 2MM
gvprof -v -e $redshow_mode $control_knobs $run_2mm &> /dev/null
echo -n "2MM $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1

########################################## 3MM #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
run_3mm="./3mm.exe"
cd ../3MM
gvprof -v -e $redshow_mode $control_knobs $run_3mm &> /dev/null
echo -n "3MM $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/3MM

version=opt
cd $APPS_DIR && cd polybench_$version
cd 3MM
gvprof -v -e $redshow_mode $control_knobs $run_3mm &> /dev/null
echo -n "3MM $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1

########################################## GRAMSCHM #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "------------------ GRAMSCHM $redshow_mode ------------------"
run_gramschm="./gramschmidt.exe"
cd GRAMSCHM
gvprof -v -e $redshow_mode $control_knobs $run_gramschm &> /dev/null
echo -n "GRAMSCHM $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/GRAMSCHM

version=opt
cd $APPS_DIR && cd polybench_$version
cd GRAMSCHM
gvprof -v -e $redshow_mode $control_knobs $run_gramschm &> /dev/null
echo -n "GRAMSCHM $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1


########################################## BICG #################################################
version=ori
cd $APPS_DIR && cd polybench_$version
echo "------------------ BICG $redshow_mode ------------------"
run_bicg="./bicg.exe"
cd BICG
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null
echo -n "BICG $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/BICG

version=opt
cd $APPS_DIR && cd polybench_$version
cd BICG
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null
echo -n "BICG $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1


################################################################################################
#################################### Profile Polybench #########################################
################################################################################################
version=ori
cd $APPS_DIR && cd simpleMultiCopy_$version && cd Samples/0_Introduction/simpleMultiCopy
echo "------------------ simpleMultiCopy $redshow_mode ------------------"
run_simpleMultiCopy="./simpleMultiCopy"
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null
echo -n "simpleMultiCopy $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
cp -r gvprof-measurements/memory_liveness/ $profile_log/simpleMultiCopy

version=opt
cd $APPS_DIR && cd simpleMultiCopy_$version && cd Samples/0_Introduction/simpleMultiCopy
gvprof -v -e $redshow_mode $control_knobs $run_bicg &> /dev/null
echo -n "simpleMultiCopy $version "
cat gvprof-measurements/memory_liveness/memory_liveness.csv | head -n 3| tail -n -1
