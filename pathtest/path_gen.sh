#!/bin/bash
# -----------------------------------------------------------------------------
# path_gen.sh
#
# Usage:
#   ./path_gen.sh func1 number1 func2 number2
# -----------------------------------------------------------------------------

set -e

MY_PATH="$(pwd)/../../../../"
export MY_PATH
# Check for jq
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is not installed. Please install jq first."
  exit 1
fi

# Check for python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed. Please install python3 first."
  exit 1
fi

# Check for opt
if ! command -v opt >/dev/null 2>&1; then
  echo "Error: opt is not installed or not in PATH."
  exit 1
fi

# Check for built-in.bc file
if [ ! -f "./built-in.bc" ]; then
  echo "Error: built-in.bc not found in current directory."
  exit 1
fi

# Check argument count
if [ $# -ne 4 ]; then
  echo "Usage: $0 func1 number1 func2 number2"
  exit 2
fi

FUNC1="$1"
NUM1="$2"
FUNC2="$3"
NUM2="$4"

DOT_FILE="built-in.bc.callgraph.dot"

# 1. Check for DOT file, generate only if missing
if [ ! -f "$DOT_FILE" ]; then
  opt -passes='dot-callgraph' built-in.bc >/dev/null 2>&1
fi

if [ ! -f "$DOT_FILE" ]; then
  echo "Error: $DOT_FILE was not generated."
  exit 3
fi

# 2. For each function, check for JSON file first, only generate if missing
for FUNC_NAME in "$FUNC1" "$FUNC2"; do
  JSON_FILE="${FUNC_NAME}.json"
  if [ ! -f "$JSON_FILE" ]; then
    python3 callgraph_to_callchain.py "$DOT_FILE" "$FUNC_NAME" "$JSON_FILE" >/dev/null 2>&1
    if [ ! -f "$JSON_FILE" ]; then
      echo "Error: $JSON_FILE was not created for function $FUNC_NAME."
      exit 4
    fi
  fi
done

# Merge the generated JSON files into pair.json
jq -s 'reduce .[] as $item ({}; . * $item)' "${FUNC1}.json" "${FUNC2}.json" > pair.json 2>/dev/null

# Generate the exactpath JSON
exact_out="${FUNC1}-${FUNC2}-exactpath.json"
python3 get_func_exactpath.py pair.json "$exact_out"

# Generate the filled source JSON
final_out="${FUNC1}-${FUNC2}.json"
python3 fill_src.py "$exact_out" "$final_out" "$NUM1" "$NUM2"