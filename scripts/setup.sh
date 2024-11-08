#!/bin/bash

choose_version() {
    while true; do
        read -p "Input your choice: " choice
        case $choice in
            1)
                echo "6.12-rc3"
                return 0
                ;;
            *)
                echo "Invalid choice, please input 1."
                ;;
        esac
    done
}

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SVF_DIR="$TOP_DIR/SVF"
LOG_DIR="$TOP_DIR/logs"

echo "Choose kernel version:"
echo "1. 6.12-rc3"
KERNEL_VER=$(choose_version)
CONFIG_DIR="$TOP_DIR/$KERNEL_VER/configs"

# create log dir
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi


# build SVF
echo "Building SVF, see logs in $LOG_DIR/SVF.log"
pushd "$SVF_DIR" > /dev/null || exit 1
source ./build.sh > "$LOG_DIR/SVF.log"
popd > /dev/null || exit 1

echo "Building Linux, see logs in $LOG_DIR/kernel_build.log"
echo "For now only support linux-6.12-rc3"
# build linux kernel bitcode files
pushd "$KERNEL_DIR" > /dev/null || exit 1
cp "$CONFIG_DIR/.config" .
cp "$CONFIG_DIR/Makefile" .
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

echo "Finish building now."