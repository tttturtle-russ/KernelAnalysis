#!/bin/bash
# -----------------------------------------------------------------------------
# path_gen.sh
#
# Script helper/tools are always referenced via $SCRIPTS_DIR.
# All input/output files are relative to the current working directory ($PWD).
#
# Usage:
#   ./path_gen.sh file1 line1 file2 line2
# -----------------------------------------------------------------------------
# set -e

# Make sure SCRIPTS_DIR is set
if [ -z "$SCRIPTS_DIR" ]; then
  echo "[Error] SCRIPTS_DIR environment variable is not set."
  exit 1
fi

if [ $# -ne 4 ]; then
  echo "Usage: $0 FILE1 NUM1 FILE2 NUM2"
  exit 2
fi

FILE1="$1"
NUM1="$2"
FILE2="$3"
NUM2="$4"
if [ "$NUM1" -ne 0 ] && [ "$NUM2" -ne 0 ] && [[ "$FILE1" != ./include/* ]]  && [[ "$FILE2" != ./include/* ]]; then
  BASE1=$(basename "$FILE1" .c)
  BASE2=$(basename "$FILE2" .c)

  # 生成tags文件
  TAGFILE1="${BASE1}.tags"
  TAGFILE2="${BASE2}.tags"

if [ ! -s "$TAGFILE1" ]; then
  ctags -x --c-kinds=f --fields=+n "$KERNEL_DIR/$FILE1" > "$TAGFILE1"
fi

if [ ! -s "$TAGFILE2" ]; then
  if [ "$FILE2" != "$FILE1" ]; then
    ctags -x --c-kinds=f --fields=+n "$KERNEL_DIR/$FILE2" > "$TAGFILE2"
  fi
fi

  # 调用 find_func.py 得到函数名
  TAGFILE1_ABS="$(pwd)/$TAGFILE1"
  TAGFILE2_ABS="$(pwd)/$TAGFILE2"

  FUNC1=$(python3 "$SCRIPTS_DIR/path/find_func.py" "$TAGFILE1_ABS" "$NUM1")
  if [ -z "$FUNC1" ]; then
    echo "[Error] Cannot find function for $FILE1:$NUM1"
    exit 3
  fi
  FUNC2=$(python3 "$SCRIPTS_DIR/path/find_func.py" "$TAGFILE2_ABS" "$NUM2")
  if [ -z "$FUNC2" ]; then
    echo "[Error] Cannot find function for $FILE2:$NUM2"
    exit 3
  fi
  # echo "[INFO] $FILE1:$NUM1 -> $FUNC1"
  # echo "[INFO] $FILE2:$NUM2 -> $FUNC2"

  DOT_FILE="$PWD/built-in.bc.callgraph.dot"

  # 1. Check for DOT file, generate only if missing
  # echo "########################################################"
  if [ ! -f "$DOT_FILE" ]; then
    echo "[INFO] Generating Callgraph...."
    opt -passes='dot-callgraph' "$PWD/built-in.bc" >/dev/null 2>&1
    echo echo "[INFO] Generating built-in.ll...."
    llvm-dis $PWD/built-in.bc  -o built-in.ll
  fi

  echo "0 Successfully got Callgraph: $DOT_FILE"
  # echo "################################################################################################################"

  # 2. For each function, check for JSON file first, only generate if missing
  # echo "[INFO] Generating Callchain of Pair...."
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
  jq -s 'reduce .[] as $item ({}; . * $item)' "$PWD/${FUNC1}.json" "$PWD/${FUNC2}.json" > "$PWD/${FUNC1}-${FUNC2}-pair.json" 2>/dev/null
  python3 "$SCRIPTS_DIR/path/prune_paths.py" "$PWD/${FUNC1}-${FUNC2}-pair.json" "$SCRIPTS_DIR/path/ioctl_handler.txt" "$PWD/built-in.ll"
  # echo "1 Successfully got Call-chain: $PWD/${FUNC1}-${FUNC2}-pair.json"
  # echo "################################################################################################################"

  # Generate the exactpath JSON
  exact_out="$PWD/${FUNC1}-${FUNC2}-exactpath.json"
  python3 "$SCRIPTS_DIR/path/get_func_exactpath.py" "$PWD/${FUNC1}-${FUNC2}-pair.json" "$exact_out"
  # echo "2 Successfully transfer to path $exact_out"
  # echo "################################################################################################################"

  # Generate the filled source JSON
  final_out="$PWD/${FUNC1}-${NUM1}-${FUNC2}-${NUM2}.json"
  # echo "[INFO] Filling Src..."
  python3 "$SCRIPTS_DIR/path/fill_src.py" "$exact_out" "$final_out" "$NUM1" "$NUM2" "$FUNC1" "$FUNC2" "$(basename "$(pwd)")"
  # echo "3 Successfully collected path: $final_out"
  # echo "################################################################################################################"

  # Generate prompt
  # echo "[INFO] Generating Prompt..."
  NEWFILE1=$(basename "$FILE1")
  NEWFILE2=$(basename "$FILE2")
  python3 "$SCRIPTS_DIR/path/prompt.py" "$FUNC1" "$FUNC2" "$(basename "$(pwd)")" "${FUNC1}-${NUM1}-${FUNC2}-${NUM2}.json" "$NEWFILE1" "$NEWFILE2" "$NUM1" "$NUM2"
  # echo "4 Successfully generated prompt: ${FILE1}_${NUM1}-${FILE2}_${NUM2}.prompt"
  # echo "################################################################################################################"

  # Clear rubbish
  # echo "[INFO] Clearing ..."
  rm ${FUNC1}.json
  if [ -f "${FUNC2}.json" ]; then
    rm ${FUNC2}.json
  fi
  
  # rm ${FUNC1}-${FUNC2}-pair.json
  # rm ${FUNC1}-${FUNC2}-pair-new.json
  # rm ${FUNC1}-${FUNC2}-exactpath.json

  # echo "5 Finish Cleaning"
  # echo "################################################################################################################"

fi