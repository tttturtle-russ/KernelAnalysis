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

# make CC=wllvm HOSTCC=wllvm defconfig
make CC=clang HOSTCC=clang defconfig
make menuconfig
make  CC=clang HOSTCC=clang KCFLAGS="-Og -g -Xclang -disable-O0-optnone -gdwarf-4 -fno-inline -Wno-error" -j"$(nproc)" > "$LOG_DIR/kernel_build.log"

popd > /dev/null || exit 1
