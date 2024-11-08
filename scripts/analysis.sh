#!/bin/bash

# Function to recursively find all directories and link .bc files
link_bc_files() {
    local dir="$1"
    
    # Find all .bc files in the current directory
    bc_files=$(find "$dir" -maxdepth 1 -name "*.bc")
    # If .bc files are found, link them together into combined.bc
    if [ -n "$bc_files" ]; then
        llvm-link $bc_files -o "$dir/combined.bc"
    fi

    # Recursively process subdirectories
    for subdir in "$dir"/*/; do
        if [ -d "$subdir" ]; then
            link_bc_files "$subdir"
        fi
    done
}

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SCRIPT_DIR="$TOP_DIR/scripts"

pushd "$KERNEL_DIR" > /dev/null || exit 1
# first let's link all single bcfiles into one
link_bc_files ./drivers

find . -name "combined.bc" | while read -r bcfile; do
    dir=$(dirname "$bcfile")
    name=$(dirname "$bcfile" | awk -F/ '{print $NF}')
    wpa -ander -cxt -opt-svfg -race -stat=false -dump-mssa -ind-call-limit=100000 -svfg "$bcfile" > "$dir/mssa.$name"
done;

find . -name "mssa.*" | while read -r mssa; do
    dir=$(dirname "$mssa")
    name=$(dirname "$mssa" | awk -F/ '{print $NF}')
    python3 "$SCRIPT_DIR/gen_mempair.py" "$mssa" > "$dir/mempairs.$name"
done;

popd > /dev/null || exit 1