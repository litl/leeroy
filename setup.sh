#!/bin/bash

VIRTUALENV_PATH=virtualenv

VIRTUALENV_INSTALLED=`which virtualenv`
if [ "$VIRTUALENV_INSTALLED" == "" ]; then
    echo -e "virtualenv NOT found."
    exit 1
fi

if [ -f $VIRTUALENV_PATH/requirements.txt ]; then
    if diff $VIRTUALENV_PATH/requirements.txt requirements.txt | grep -q ^\<; then
        echo "Need to regenerate virtualenv due to changes in requirements.txt"
        rm -rf $VIRTUALENV_PATH
    fi
fi

if [ "$PIP_DOWNLOAD_CACHE" == "" ]; then
    export PIP_DOWNLOAD_CACHE="~/.pip_download_cache"
fi

EXISTING_ENV=$VIRTUAL_ENV
virtualenv --no-site-packages $VIRTUALENV_PATH

cat >> $VIRTUALENV_PATH/bin/activate <<EOF

# litl customization for prompt to not suck
if [ -z "\$VIRTUAL_ENV_DISABLE_PROMPT" ]; then
    export PS1="(\$(basename \$(dirname \"\$VIRTUAL_ENV\")))\$_OLD_VIRTUAL_PS1"
fi
EOF

source $VIRTUALENV_PATH/bin/activate

# Tweaking ARCHFLAGS is necessary on mac because otherwise pip tries to build
# coverage for the ppc architecture, which is not supported by xcode 4. See
# http://stackoverflow.com/questions/5256397/osx-10-6-6-cant-install-appscript
if [ "$(uname)" = "Darwin" ] ; then
    export ARCHFLAGS="-arch i386 -arch x86_64"
fi

python setup.py develop

cp requirements.txt $VIRTUALENV_PATH

if [ "$EXISTING_ENV" == "" ]; then
    echo "Run \"source $VIRTUALENV_PATH/bin/activate\" to activate this virtualenv."
fi
