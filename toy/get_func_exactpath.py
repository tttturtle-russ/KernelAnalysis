#!/usr/bin/env python3
import os
import json
import re
import subprocess
import sys

INPUT_JSON = sys.argv[1] if len(sys.argv) > 1 else "pair.json"
OUTPUT_JSON = sys.argv[2] if len(sys.argv) > 2 else "pair_exactpath.json"
EXTRACT_SCRIPT = "./extract-func.sh"

def extract_func_ll(func):
    ll_file = f"{func}.ll"
    if os.path.exists(ll_file):
        return
    ret = subprocess.run([EXTRACT_SCRIPT, func])
    if ret.returncode != 0:
        raise RuntimeError(f"extract-func.sh failed for function: {func}")

def get_source_path_line_from_ll(func):
    ll_file = f"{func}.ll"
    if not os.path.exists(ll_file):
        raise FileNotFoundError(f"{ll_file} does not exist after extraction.")

    with open(ll_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Find !DISubprogram(name: "<func>"
    disub_line = None
    for line in lines:
        if f'!DISubprogram(name: "{func}"' in line:
            disub_line = line
            break
    if not disub_line:
        raise RuntimeError(f"Cannot find !DISubprogram(name: \"{func}\") in {ll_file}")

    # Find file: !<number>
    m_file = re.search(r'file: !(\d+)', disub_line)
    if not m_file:
        raise RuntimeError(f"Cannot find file metadata in DISubprogram line for {func}")
    file_num = m_file.group(1)

    # Find line: <number>
    m_line = re.search(r'line: (\d+)', disub_line)
    if not m_line:
        raise RuntimeError(f"Cannot find line number in DISubprogram line for {func}")
    line_number = m_line.group(1)

    # Find !<number> = !DIFile(filename: "...", directory: "...")
    file_line = None
    for line in lines:
        if re.match(fr'!{file_num}\s*=\s*!DIFile\(', line):
            file_line = line
            break
    if not file_line:
        raise RuntimeError(f"Cannot find DIFile metadata !{file_num} for {func}")

    m = re.search(r'filename: "([^"]+)", directory: "([^"]+)"', file_line)
    if not m:
        raise RuntimeError(f"Cannot extract filename and directory in DIFile for {func}")
    filename, directory = m.group(1), m.group(2)

    # Standardize path
    source_path = os.path.normpath(os.path.join(directory, filename))
    source_path = source_path.replace('\\', '/')
    return f"{source_path}:{line_number}  {func}"

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[ERROR] Input file {INPUT_JSON} not found.")
        return
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Step 1: Collect all unique function names
    unique_funcs = set()
    for paths in data.values():
        for path in paths:
            for func in path:
                unique_funcs.add(func)

    # Step 2: Build func_name -> "path:line  func" mapping
    func2exactinfo = dict()
    for func in unique_funcs:
        try:
            extract_func_ll(func)
            info = get_source_path_line_from_ll(func)
            func2exactinfo[func] = info
            print(f"[OK] {func}: {info}")
        except Exception as e:
            print(f"[ERROR] Failed to process function {func}: {e}")
            exit(1)

    # Step 3: Replace all func names in all paths
    new_data = dict()
    for key, paths in data.items():
        new_paths = []
        for path in paths:
            new_path = [func2exactinfo[func] for func in path]
            new_paths.append(new_path)
        new_data[key] = new_paths

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()