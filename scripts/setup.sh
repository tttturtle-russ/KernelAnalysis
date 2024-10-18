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
pushd "$SVF_DIR" > /dev/null || exit 1
source ./build.sh > "$LOG_DIR/SVF.log"
popd > /dev/null || exit 1

# build linux kernel bitcode files
pushd "$KERNEL_DIR" > /dev/null || exit 1
make defconfig
# disable warnings as errors
./scripts/config --disable CONFIG_WERROR
make CC=clang \
    LD=ld.lld \
    AR=llvm-ar \
    NM=llvm-nm \
    STRIP=llvm-strip \
    OBJCOPY=llvm-objcopy \
    OBJDUMP=llvm-objdump \
    READELF=llvm-readelf \
    HOSTCC=clang \
    HOSTCXX=clang++ \
    HOSTAR=llvm-ar \
    HOSTLD=ld.lld \
    V=0 \
    -j"$(nproc)" > "$LOG_DIR/kernel_build.log"
popd > /dev/null || exit 1
