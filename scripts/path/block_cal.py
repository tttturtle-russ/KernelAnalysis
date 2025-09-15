import sys
import json
import re
import os

def parse_ll_blocks(ll_path):
    func_blocks = {}
    current_func = None
    block_count = 0
    in_func = False
    # 更通用的函数头识别
    func_pattern = re.compile(r'^define\s+.*@([^\s(]+)\s*\(')
    # 匹配左对齐的label（不缩进且以:结尾且不是指令）
    block_pattern = re.compile(r'^([a-zA-Z0-9_.$]+):\s*(;.*)?$')

    with open(ll_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 检查函数开始
            func_match = func_pattern.match(line)
            if func_match:
                current_func = func_match.group(1)
                block_count = 0
                in_func = True
                continue

            if in_func:
                # 检查block label
                block_match = block_pattern.match(line)
                if block_match:
                    block_count += 1
                # 检查函数结束
                if line.strip() == '}':
                    func_blocks[current_func] = block_count
                    in_func = False
    return func_blocks

def main():
    if len(sys.argv) != 2:
        print("Usage: python ll2blocks.py input.ll")
        sys.exit(1)

    llfile = sys.argv[1]
    jsonfile = os.path.splitext(llfile)[0] + ".json"

    func_blocks = parse_ll_blocks(llfile)

    with open(jsonfile, 'w', encoding='utf-8') as f:
        json.dump(func_blocks, f, indent=2, ensure_ascii=False)

    print(f"已输出 {jsonfile}")

if __name__ == "__main__":
    main()