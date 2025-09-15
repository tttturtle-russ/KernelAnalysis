#!/usr/bin/env python3
import os
import json
import re
import subprocess
import sys

INPUT_JSON = sys.argv[1] if len(sys.argv) > 1 else "pair.json"
OUTPUT_JSON = sys.argv[2] if len(sys.argv) > 2 else "pair_exactpath.json"
BUILTIN_LL = "built-in.ll"

def parse_builtin_ll(builtin_ll_content):
    funcname2fileline = {}
    filenum2file = {}

    # !DISubprogram
    disub_re = re.compile(r'!DISubprogram\(name: "([^"]+)"[^)]*file: !(\d+)[^)]*line: (\d+)[^)]*\)')
    for m in disub_re.finditer(builtin_ll_content):
        funcname, file_num, line_number = m.group(1), m.group(2), m.group(3)
        funcname2fileline[funcname] = (file_num, line_number)

    # !DIFile
    difile_re = re.compile(
        r'!(\d+)\s*=\s*!DIFile\(\s*filename: "([^"]+)",\s*directory: "([^"]+)"[^)]*\)'
    )
    for m in difile_re.finditer(builtin_ll_content):
        file_num, filename, directory = m.group(1), m.group(2), m.group(3)
        filenum2file[file_num] = (filename, directory)

    return funcname2fileline, filenum2file

def get_source_path_line_from_index(func, funcname2fileline, filenum2file):
    """
    从预处理好的索引字典高效查找
    """
    if func not in funcname2fileline:
        raise RuntimeError(f"Cannot find {func} in DISubprogram.")

    file_num, line_number = funcname2fileline[func]

    if file_num not in filenum2file:
        raise RuntimeError(f"Cannot find file_num {file_num} in DIFile.")

    filename, directory = filenum2file[file_num]
    source_path = os.path.normpath(os.path.join(directory, filename))
    source_path = source_path.replace('\\', '/')
    return f"{source_path}:{line_number}"

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[ERROR] Input file {INPUT_JSON} not found.")
        return

    # Check if built-in.ll exists, if not generate it from built-in.bc
    if not os.path.exists(BUILTIN_LL):
        # print(f"[INFO] {BUILTIN_LL} not found, generating from built-in.bc...")
        ret = subprocess.run(["llvm-dis", "built-in.bc", "-o", BUILTIN_LL])
        if ret.returncode != 0:
            print(f"[ERROR] Failed to generate {BUILTIN_LL} from built-in.bc")
            return

    # Read built-in.ll content once
    # print(f"[INFO] Reading {BUILTIN_LL}...")
    with open(BUILTIN_LL, "r", encoding="utf-8", errors="ignore") as f:
        builtin_ll_content = f.read()

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Step 1: Collect all unique function names
    unique_funcs = set()
    for paths in data.values():
        for path in paths:
            for func in path:
                unique_funcs.add(func)

    # Step 2: 预解析 built-in.ll，建立索引字典
    funcname2fileline, filenum2file = parse_builtin_ll(builtin_ll_content)

    # Step 3: Build func_name -> "path:line  func" mapping
    func2exactinfo = dict()
    for func in unique_funcs:
        try:
            info = get_source_path_line_from_index(func, funcname2fileline, filenum2file)
            # print(f"[OK] {func}: {info}")
        except Exception as e:
            print(f"[ERROR] Failed to process function {func}: {e}")
            exit(1)
        func2exactinfo[func] = f"{info}  {func}"  # 保持原始输出格式

    # Step 4: Replace all func names in all paths
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