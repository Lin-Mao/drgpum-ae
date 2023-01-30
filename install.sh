#/bin/bash

APPS_DIR=$AE_ROOT/apps

ARCH=86

if [ -n "$1" ]; then
    ARCH=$1
fi

cd $APPS_DIR

################################################################################################
#################################### Install Darknet ###########################################
################################################################################################
# original version
git clone https://github.com/AppCases/darknet.git darknet_ori && cd darknet_ori
git checkout gpu
make -f makefile_sm$ARCH -j

wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights

# optimized version
cd ..
cp -r darknet_ori darknet_opt && cd darknet_opt
git checkout dev

make clean
make -f makefile_sm$ARCH -j

