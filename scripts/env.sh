#!/bin/bash
# root
export AE_ROOT=/root
export APPS_DIR=$AE_ROOT/applications

# openmpi
export PATH=/root/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/root/openmpi/lib:$LD_LIBRARY_PATH

# DrGPUM
export DRGPUM_PATH=$AE_ROOT/DrGPUM/gvprof
export PATH=${DRGPUM_PATH}/bin:$PATH
export PATH=${DRGPUM_PATH}/hpctoolkit/bin:$PATH
export PATH=${DRGPUM_PATH}/redshow/bin:$PATH

