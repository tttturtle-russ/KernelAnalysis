#!/bin/bash

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SVF_DIR="$TOP_DIR/SVF"
LOG_DIR="$TOP_DIR/logs"

# create log dir
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

# setup virtualenv
echo "Setting up virtualenv"
python3 -m venv venv
source venv/bin/activate


