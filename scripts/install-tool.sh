#!/bin/bash
## install pytorch
export AE_ROOT=/root
eval "$($AE_ROOT/anaconda3/bin/conda shell.bash hook)"
conda create -n torch python=3.8 -y
conda activate torch
conda install astunparse numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing_extensions future six requests dataclasses -y
conda install -c pytorch magma-cuda116 -y

cd $AE_ROOT

git clone --recursive https://github.com/AppCases/pytorch.git
cd pytorch
git submodule sync
git submodule update --init --recursive --jobs 0
cd ../ && cp -r pytorch pytorch-opt && cd pytorch

export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
export USE_CUDA=1
export REL_WITH_DEB_INFO=1
export MAX_JOBS=$(nproc --all)
export USE_NINJA=OFF
python setup.py install

# cd ../ && cd pytorch-opt
# conda deactivate
# conda create -n torch-opt python=3.8 -y
# conda activate torch-opt
# conda install astunparse numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing_extensions future six requests dataclasses -y
# conda install -c pytorch magma-cuda116 -y

# python setup.py install

## install tool
export PYTORCH_DIR=$AE_ROOT/pytorch/torch

cd $AE_ROOT

git clone --recursive https://github.com/Lin-Mao/DrGPUM.git
cd DrGPUM
git submodule sync
git submodule update --init --recursive --jobs 0
./bin/install

