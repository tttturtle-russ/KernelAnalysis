#!/bin/bash

# create log dir
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

# build SVF
pushd "$SVF_DIR" > /dev/null || exit 1
source ./build.sh > "$LOG_DIR/SVF.log"
popd > /dev/null || exit 1

# setup virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip3 install -r requirements.txt

# build linux kernel bitcode files
pushd "$KERNEL_DIR" > /dev/null || exit 1

make CC=wllvm HOSTCC=wllvm KCFLAGS="-Og -g -Xclang -disable-O0-optnone -fno-inline" -j"$(nproc)" drivers/ > "$LOG_DIR/kernel_build.log"
find drivers -name "*.a" | while read -r archive; do
        extract-bc -b "$archive"
        if [ ! -f "$archive".bc ]; then
                continue
        fi
        dir_name=$(dirname "$archive")
        mv "$archive".bc "$dir_name"/$(basename "$archive" .a).bc
done
popd > /dev/null || exit 1
