#!/bin/bash

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SVF_DIR="$TOP_DIR/SVF"
LOG_DIR="$TOP_DIR/logs"

# create log dir
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi


# build SVF
echo "Building SVF, see logs in $LOG_DIR/SVF.log"
pushd "$SVF_DIR" > /dev/null || exit 1
source ./build.sh > "$LOG_DIR/SVF.log"
popd > /dev/null || exit 1

# setup virtualenv
echo "Setting up virtualenv"
python3 -m venv venv
source venv/bin/activate

# install wllvm
echo "Installing wllvm"
pip3 install wllvm
export LLVM_COMPILER=clang

echo "Building Linux, see logs in $LOG_DIR/kernel_build.log"
echo "For now only support linux-6.12-rc7"
# build linux kernel bitcode files
pushd "$KERNEL_DIR" > /dev/null || exit 1

make CC=wllvm HOSTCC=wllvm defconfig
# make CC=wllvm HOSTCC=wllvm -j"$(nproc)" drivers/ > "$LOG_DIR/kernel_build.log"
make CC=wllvm HOSTCC=wllvm KCFLAGS="-Og -g -Xclang -disable-O0-optnone -fno-inline" -j"$(nproc)" drivers/ > "$LOG_DIR/kernel_build.log"
for dir in drivers/*; do
        if [ -d "$dir" ]; then
                if [ ! -f "$dir/built-in.a" ]; then
                        continue
                else
                        find "$dir" -name built-in.a | while read -r archive; do
                                extract-bc -b "$archive"
                                if [ ! -f "$archive".bc ]; then
                                        continue
                                fi
                                dir_name=$(dirname "$archive")
                                mv "$archive".bc "$dir_name"/built-in.bc
                        done
                fi
        fi
done
popd > /dev/null || exit 1
