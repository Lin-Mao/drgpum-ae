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

bash $SCRIPTS_PATH/install-tool.sh
bash $SCRIPTS_PATH/install-apps.sh $ARCH