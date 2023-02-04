
#!/bin/bash
export AE_ROOT=/root
export APPS_DIR=$AE_ROOT/apps

# interations for each profiling
iteration=10
# (seconds) interval between each profiling
interval=5

############################## Polybench ##############################
version=shared
cd $APPS_DIR
cd polybench_$version
git checkout heatmap &> /dev/null

############################## GRAMSCHM ##############################
echo "------------------ GRAMSCHM ori ------------------"
cd ./GRAMSCHM
make -j &> /dev/null
# warm-up
run_gramschm_ori="./gramschmidt.exe"
$run_gramschm_ori &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
$run_gramschm_ori
echo ""
done
echo ""

echo "------------------ GRAMSCHM opt ------------------"
# warm-up
run_gramschm_sharedmem="./gramschmidt_sa65.exe"
$run_gramschm_sharedmem &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
$run_gramschm_sharedmem
echo ""
done
echo ""

############################## BICG ##############################
echo "------------------ BICG ori ------------------"
cd ../BICG
make -j &> /dev/null
# warm-up
run_bicg_ori="./bicg.exe"
$run_bicg_ori &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
$run_bicg_ori
echo ""
done
echo ""

echo "------------------ BICG opt ------------------"
# warm-up
run_bicg_sharedMem="./bicg_shareMem.exe"
$run_bicg_sharedMem &> /dev/null

for ((i = 0; i < $iteration; i++))
do
echo "$((i+1)) round"
sleep $interval
$run_bicg_sharedMem
echo ""
done
echo ""
echo "------------------ END ------------------"