#!/bin/bash

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SCRIPT_DIR="$TOP_DIR/scripts"

pushd "$KERNEL_DIR" >/dev/null || exit 1

find . -mindepth 3 -maxdepth 3 -name "built-in.bc" | while read -r bcfile; do
  dir=$(dirname "$bcfile")
  name=$(dirname "$bcfile" | awk -F/ '{print $NF}')
  if [ -f "$dir/mssa.$name" ]; then
    echo "Skipping $name"
    continue
  fi
  echo "Analyzing $name"
  wpa -fspta -cxt -race -stat=false -dump-mssa -ind-call-limit=100000 "$bcfile" >"$dir/mssa.$name"
done

find . -mindepth 3 -maxdepth 3 -name "mssa.*" | while read -r mssa; do
  dir=$(dirname "$mssa")
  name=$(dirname "$mssa" | awk -F/ '{print $NF}')
  echo "Generating $name"
  python3 "$SCRIPT_DIR/gen_mempair.py" "$mssa" "$dir/mempairs.$name" "$dir/mapping.$name"
done

find . -mindepth 3 -maxdepth 3 -name "mempairs.*" -exec sh -c "sort {} | uniq" \; >mempairs_all
sort mempairs_all | uniq >mempairs_uniq

popd >/dev/null || exit 1
