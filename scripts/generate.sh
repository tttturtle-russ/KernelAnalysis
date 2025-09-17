#!/bin/bash

# This script generates prompts with path information 
# and feeds them to the LLM and then generates C source code
# then get the corresponding ip of each target line

WORKDIR="$SCRIPTS_DIR/path/workdir"
PATH_GEN_SCRIPT="../../path_gen.sh"

if [ ! -d "$WORKDIR" ]; then
    mkdir -p "$WORKDIR"
fi

## 1. Clear the format of the pair.list
INPUT_FILE="$KERNEL_DIR/ka_mempairs_test-2"
# OUTPUT_FILE="$KERNEL_DIR/ka_test_uniq.cleaned"
# sed -e 's/:/ /g' -e 's/->W//g' -e 's/->R//g' "$INPUT_FILE" > "$OUTPUT_FILE"

## 2. Deal with each line
while read -r line; do
    line="${line//:/' '}"
    line="${line//->/' '}"
    read -r FILE1 NUM1 RW1 FILE2 NUM2 RW2 <<< "$line"
    if [ "$NUM1" -ne 0 ] && [ "$NUM2" -ne 0 ] && [[ "$FILE1" != ./include/* ]] && [[ "$FILE2" != ./include/* ]]; then
        # Extract the driver from the pair
        DRIVER_SUBDIR=$(echo "$FILE1" | cut -d'/' -f2)
        # Target dir in workdir
        SUBDIR_PATH="$WORKDIR/$DRIVER_SUBDIR"
        # if not exist, create and copy built-in.bc
        if [ ! -d "$SUBDIR_PATH" ]; then
            mkdir -p "$SUBDIR_PATH"
            cp "$KERNEL_DIR/drivers/$DRIVER_SUBDIR/built-in.bc" "$SUBDIR_PATH/"
        fi
        pushd "$SUBDIR_PATH" > /dev/null || exit 1
        $PATH_GEN_SCRIPT "$FILE1" "$NUM1" "$FILE2" "$NUM2"
        popd > /dev/null || exit 1
        # filename1=$(basename "$FILE1")
        # filename2=$(basename "$FILE2")
        # IP_FILE_PATH_1="$SUBDIR_PATH/$filename1"_"$NUM1".ip
        # IP_FILE_PATH_2="$SUBDIR_PATH/$filename2"_"$NUM2".ip
        # if [ "$RW1" == "W" ] && [ ! -f $IP_FILE_PATH_1 ]; then
        #     python3 "$SCRIPTS_DIR"/get_ip.py "$FILE1:$NUM1" >> $IP_FILE_PATH_1
        #     if [ ! -s $IP_FILE_PATH_1 ]; then
        #         rm $IP_FILE_PATH_1
        #     fi
        # fi
        # if [ "$RW2" == "W" ] && [ ! -f $IP_FILE_PATH_2 ]; then
        #     python3 "$SCRIPTS_DIR"/get_ip.py "$FILE2:$NUM2" >> $IP_FILE_PATH_2
        #     if [ ! -s $IP_FILE_PATH_2 ]; then
        #         rm $IP_FILE_PATH_2
        #     fi
        # fi
    fi
done < "$INPUT_FILE"