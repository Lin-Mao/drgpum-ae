#/bin/bash


export AE_ROOT=/root
export SCRIPTS_PATH=$AE_ROOT/scripts

if [ -n "$1" ]; then
    ARCH=$1
fi

if [ -z "$ARCH" ]
then
    echo "Please specify Arch [3090: 86, A100: 80]."
    exit
fi

# get update-to-date scripts
cd $AE_ROOT
git clone https://github.com/Lin-Mao/drgpum-ae.git &> /dev/null
rm -rf $SCRIPTS_PATH/python
cd drgpum-ae/scripts/ && rm install.sh && mv ./* $SCRIPTS_PATH/
cd $AE_ROOT
rm -rf drgpum-ae

bash $SCRIPTS_PATH/install-tool.sh
bash $SCRIPTS_PATH/install-apps.sh $ARCH