#/bin/bash
ARCH=80
export AE_ROOT=/root
export PATH=/root/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/root/openmpi/lib:$LD_LIBRARY_PATH

if [ -n "$1" ]; then
    ARCH=$1
fi
APPS_DIR=$AE_ROOT/apps

mkdir $APPS_DIR

################################################################################################
#################################### Install Darknet ###########################################
################################################################################################
cd $APPS_DIR
# original version
git clone https://github.com/AppCases/darknet.git darknet_ori && cd darknet_ori
git checkout gpu
make -f makefile_sm$ARCH -j

wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights

# optimized version
cd .. && cp -r darknet_ori darknet_opt && cd darknet_opt
git checkout dev

make clean
make -f makefile_sm$ARCH -j

################################################################################################
##################################### Install Laghos ###########################################
################################################################################################
cd $APPS_DIR
mkdir laghos_ori
cd laghos_ori && git clone https://github.com/AppCases/Laghos.git
cd Laghos && git checkout cuda

make setup NPROC=16 MFEM_BUILD="pcuda CUDA_ARCH='sm_$ARCH -lineinfo' BASE_FLAGS='-std=c++11 -g'"
make -j

# optimized
cd ../../ && cp -r laghos_ori laghos_opt
cd laghos_opt/mfem && git checkout liveness_opt
cd ../Laghos && git checkout liveness_opt

make setup NPROC=16 MFEM_BUILD="pcuda CUDA_ARCH='sm_$ARCH -lineinfo' BASE_FLAGS='-std=c++11 -g'"
make -j

################################################################################################
#################################### Install miniMDock #########################################
################################################################################################
cd $APPS_DIR
# original
export GPU_INCLUDE_PATH=/usr/local/cuda/include
export GPU_LIBRARY_PATH=/usr/local/cuda/lib64
git clone https://github.com/AppCases/miniMDock.git miniMDock_ori  && cd miniMDock_ori
git checkout cuda

make DEVICE=GPU API=CUDA CARD=NVIDIA

# optimized
cd .. && cp -r miniMDock_ori miniMDock_opt && cd miniMDock_opt
git checkout main
make DEVICE=GPU API=CUDA CARD=NVIDIA

################################################################################################
#################################### Install Polybench #########################################
################################################################################################
cd $APPS_DIR
git clone https://github.com/AppCases/polybench-gpu.git polybench_ori
cp -r polybench_ori polybench_opt
cp -r polybench_ori polybench_shared

# original
cd polybench_ori && git checkout cuda

make -j
rm -rf 2DCONV 3DCONV ATAX CORR FDTD-2D COVAR GEMM GESUMMV MVT SYR2K SYRK

# optimized
cd ../polybench_opt && git checkout dev

make -j 
rm -rf 2DCONV 3DCONV ATAX CORR FDTD-2D COVAR GEMM GESUMMV MVT SYR2K SYRK

# shared memory speedup
cd ../polybench_shared && git checkout heatmap

make -j 
rm -rf 2DCONV 3DCONV ATAX CORR FDTD-2D COVAR GEMM GESUMMV MVT SYR2K SYRK

################################################################################################
##################################### Install Rodinia ##########################################
################################################################################################
cd $APPS_DIR
git clone https://github.com/AppCases/Rodinia.git rodinia_ori
cd rodinia_ori && git checkout gpu && ./get_data.sh && cd ..
cp -r rodinia_ori rodinia_opt

# original
cd rodinia_ori && git checkout gpu
rm -rf backprop cfd bfs gaussian heartwall hotspot hotspot3D \
hybridsort kmeans lavaMD leukocyte lud nn nw mummergpu myocyte \
particlefilter pathfinder streamcluster srad b+tree

cd huffman
make SM=sm_$ARCH -j

cd ../dwt2d && make GPU_ARCH=-arch=sm_$ARCH -j
cd ../../

cd rodinia_opt && git checkout dev
rm -rf backprop cfd bfs gaussian heartwall hotspot hotspot3D \
hybridsort kmeans lavaMD leukocyte lud nn nw mummergpu myocyte \
particlefilter pathfinder streamcluster srad

cd huffman
make SM=sm_$ARCH -j

cd ../dwt2d && make GPU_ARCH=-arch=sm_$ARCH -j
cd ../../


################################################################################################
##################################### Install XSBench ##########################################
################################################################################################
cd $APPS_DIR
git clone https://github.com/AppCases/XSBench.git XSBench_ori
cp -r XSBench_ori XSBench_opt

# original
cd XSBench_ori/cuda && git checkout cuda
make -f makefile_sm$ARCH -j

# optimized
cd ../../
cd XSBench_opt/cuda && git checkout dev
make SM_VERSION=$ARCH -j


################################################################################################
################################# Install simpleMultiCopy ######################################
################################################################################################
cd $APPS_DIR
git clone https://github.com/AppCases/cuda-samples.git simpleMultiCopy_ori
cp -r simpleMultiCopy_ori simpleMultiCopy_opt

# original
cd simpleMultiCopy_ori && git checkout ori && cd Samples/0_Introduction/simpleMultiCopy
make -j

# optimized
cd ../../../../
cd simpleMultiCopy_opt && git checkout opt && cd Samples/0_Introduction/simpleMultiCopy
make -j
