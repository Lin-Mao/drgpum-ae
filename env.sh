#!/bin/bash
export AE_ROOT=/home/lm/asplos23-ae
export APPS_DIR=$AE_ROOT/apps

# export PYTORCH_DIR=xxx

export DRGPUM_ROOT=/home/lm/DrGPUM/gvprof
export PATH=${DRGPUM_ROOT}/bin:$PATH
export PATH=${DRGPUM_ROOT}/hpctoolkit/bin:$PATH
export PATH=${DRGPUM_ROOT}/redshow/bin:$PATH