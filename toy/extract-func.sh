#!/bin/bash
# -----------------------------------------------------------------------------
# extract-one-func.sh
#
# This script extracts a specified function from a LLVM bitcode file
# named 'built-in.bc' in the current directory.
# It uses llvm-extract to generate a .bc file containing only the function
# and its dependencies.
# If <function_name>.bc already exists, extraction is skipped.
# After extracting .bc, if <function_name>.ll does not exist, it is generated
# from the .bc file using llvm-dis. The intermediate .bc file is deleted after .ll is generated.
#
# Usage:
#   ./extract-one-func.sh <function_name>
# -----------------------------------------------------------------------------

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <function_name>"
    exit 1
fi

FUNC="$1"
BC_FILE="built-in.bc"
OUT_BC="${FUNC}.bc"
OUT_LL="${FUNC}.ll"

if [ ! -f "$BC_FILE" ]; then
    echo "Error: $BC_FILE not found in the current directory."
    exit 2
fi

if [ ! -f "$OUT_BC" ]; then
    llvm-extract -func="$FUNC" "$BC_FILE" -o "$OUT_BC"
    if [ $? -ne 0 ]; then
        echo "Extraction failed for $FUNC. Please check the function name and the .bc file."
        exit 3
    fi
fi

if [ ! -f "$OUT_LL" ]; then
    llvm-dis "$OUT_BC" -o "$OUT_LL"
    if [ $? -ne 0 ]; then
        echo "Generation of $OUT_LL failed!"
        exit 4
    fi
    rm -f "$OUT_BC"
fi