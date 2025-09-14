#!/bin/bash
PROJECT_ROOT=../..
VENVDIR=$PROJECT_ROOT/.venv-linux
if [ -d $VENVDIR ]; then
    echo "Using python virtualenv at $VENVDIR"
else
    echo "Creating python virtualenv at $VENVDIR"
    python3 -m venv $VENVDIR
    $VENVDIR/bin/pip install -r requirements.txt
fi
$VENVDIR/bin/python3 __main__.py
