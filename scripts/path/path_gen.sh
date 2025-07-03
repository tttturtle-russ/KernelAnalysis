#!/bin/bash
# -----------------------------------------------------------------------------
# path_gen.sh
#
# Script helper/tools are always referenced via $SCRIPTS_DIR.
# All input/output files are relative to the current working directory ($PWD).
#
# Usage:
#   ./path_gen.sh func1 number1 func2 number2
# -----------------------------------------------------------------------------

set -e

# Make sure SCRIPTS_DIR is set
if [ -z "$SCRIPTS_DIR" ]; then
  echo "[Error] SCRIPTS_DIR environment variable is not set."
  exit 1
fi

export MY_PATH=/home/kddrca/

# Check for jq
if ! command -v jq >/dev/null 2>&1; then
  echo "[Error] jq is not installed. Please install jq first."
  exit 1
fi

# Check for python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "[Error] python3 is not installed. Please install python3 first."
  exit 1
fi

# Check for opt
if ! command -v opt >/dev/null 2>&1; then
  echo "[Error] opt is not installed or not in PATH."
  exit 1
fi

# Check for built-in.bc file in current working directory
if [ ! -f "$PWD/built-in.bc" ]; then
  echo "[Error] built-in.bc not found in current working directory."
  exit 1
fi

# Check for llvm-dis
if ! command -v llvm-dis >/dev/null 2>&1; then
  echo "[Error] llvm-dis is not installed or not in PATH."
  exit 1
fi

if [ $# -ne 4 ]; then
  echo "Usage: $0 func1 number1 func2 number2"
  exit 2
fi

FUNC1="$1"
NUM1="$2"
FUNC2="$3"
NUM2="$4"

DOT_FILE="$PWD/built-in.bc.callgraph.dot"

# 1. Check for DOT file, generate only if missing
echo "########################################################"
if [ ! -f "$DOT_FILE" ]; then
  echo "[INFO] Generating Callgraph...."
  opt -passes='dot-callgraph' "$PWD/built-in.bc" >/dev/null 2>&1
fi

if [ ! -f "$DOT_FILE" ]; then
  echo "[Error] $DOT_FILE was not generated."
  exit 3
fi


echo "0 Successfully got Callgraph: $DOT_FILE"
echo "################################################################################################################"

# 2. For each function, check for JSON file first, only generate if missing
echo "[INFO] Generating Callchain of Pair...."
for FUNC_NAME in "$FUNC1" "$FUNC2"; do
  JSON_FILE="$PWD/${FUNC_NAME}.json"
  if [ ! -f "$JSON_FILE" ]; then
    python3 "$SCRIPTS_DIR/path/callgraph_to_callchain.py" "$DOT_FILE" "$FUNC_NAME" "$JSON_FILE" # >/dev/null 2>&1
    if [ ! -f "$JSON_FILE" ]; then
      echo "[Error] $JSON_FILE was not created for function $FUNC_NAME."
      exit 4
    fi
  fi
done

# Merge the generated JSON files into pair.json
jq -s 'reduce .[] as $item ({}; . * $item)' "$PWD/${FUNC1}.json" "$PWD/${FUNC2}.json" > "$PWD/pair.json" 2>/dev/null
echo "1 Successfully got Call-chain: $PWD/pair.json"
echo "################################################################################################################"

# Generate the exactpath JSON
exact_out="$PWD/${FUNC1}-${FUNC2}-exactpath.json"
python3 "$SCRIPTS_DIR/path/get_func_exactpath.py" "$PWD/pair.json" "$exact_out"
echo "2 Successfully transfer to path $exact_out"
echo "################################################################################################################"

# Generate the filled source JSON
final_out="$PWD/${FUNC1}-${FUNC2}.json"
echo "[INFO] Filling Src..."
python3 "$SCRIPTS_DIR/path/fill_src.py" "$exact_out" "$final_out" "$NUM1" "$NUM2"
echo "3 Successfully collected path: $final_out"
echo "################################################################################################################"