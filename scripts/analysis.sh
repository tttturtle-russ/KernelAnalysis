#!/bin/bash

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SCRIPT_DIR="$TOP_DIR/scripts"

find_and_merge_mempair() {
    find . -mindepth 3 -maxdepth 3 -name "mempairs.*" -exec sh -c "sort {} | uniq" \; >mempairs_all
    sort mempairs_all | uniq >mempairs_uniq
}

find_and_merge_mapping() {
    find . -mindepth 3 -maxdepth 3 -name "mapping.*" -exec sh -c "sort {} | uniq" \; >mapping_all
    sort mapping_all | uniq >mapping_uniq
}

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

# use parallel to speed up
export -f find_and_merge_mempair find_and_merge_mapping
parallel --jobs 2 ::: find_and_merge_mempair find_and_merge_mapping

popd >/dev/null || exit 1
