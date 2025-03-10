#!/bin/bash

TOP_DIR="$(pwd)/.."
KERNEL_DIR="$TOP_DIR/linux"
SCRIPT_DIR="$TOP_DIR/scripts"

find_and_merge_mempairs() {
    find . -mindepth 3 -maxdepth 3 -name "ka_mempairs.*" -exec sh -c 'cat "$1' _ {} \; > ka_mempairs_all
    sort ka_mempairs_all | uniq > ka_mempairs_uniq
}

find_and_merge_mapping() {
    find . -mindepth 3 -maxdepth 3 -name "ka_mapping.*" -exec sh -c 'cat "$1"' _ {} \; > ka_mapping_all
    sort ka_mapping_all | uniq > ka_mapping_uniq
}

pushd "$KERNEL_DIR" >/dev/null || exit 1

find . -mindepth 3 -maxdepth 3 -name "built-in.bc" | while read -r bcfile; do
  dir=$(dirname "$bcfile")
  name=$(dirname "$bcfile" | awk -F/ '{print $NF}')
  if [ -f "$dir/ka_mssa.$name" ]; then
    echo "Skipping $name"
    continue
  fi
  echo "Analyzing $name"
  wpa -fspta -cxt -race -stat=false -dump-mssa -ind-call-limit=100000 "$bcfile" >"$dir/ka_mssa.$name"
done

find . -mindepth 3 -maxdepth 3 -name "ka_mssa.*" | while read -r mssa; do
  dir=$(dirname "$mssa")
  name=$(dirname "$mssa" | awk -F/ '{print $NF}')
  echo "Generating $name"
  python3 "$SCRIPT_DIR/gen_mempair.py" "$mssa" "$dir/ka_mempairs.$name" "$dir/ka_mapping.$name"
done

# use parallel to speed up
echo "Start finding and merging mempairs and mappings"
export -f find_and_merge_mempairs find_and_merge_mapping
parallel --jobs 2 ::: find_and_merge_mempairs find_and_merge_mapping

popd >/dev/null || exit 1
