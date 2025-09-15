import sys
import json
import re

def load_ioctl_handlers(txtfile):
    handlers = set()
    with open(txtfile, 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip()
            if name:
                handlers.add(name)
    return handlers

def parse_ll_functions(llfile):

    func_bodies = {}
    with open(llfile, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    func_name = None
    func_lines = []
    in_func = False

    func_header_re = re.compile(r'^define\s.*@([^(]+)\(')
    for line in lines:
        if not in_func:
            m = func_header_re.match(line)
            if m:
                func_name = m.group(1)
                in_func = True
                func_lines = [line]
        else:
            func_lines.append(line)
            if line.strip() == '}':
                if func_name:
                    func_bodies[func_name] = list(func_lines)
                func_name = None
                func_lines = []
                in_func = False
    return func_bodies

def count_blocks_between_calls(func_lines, target_func):

    block_count = 0
    found_call = False
    label_re = re.compile(r'^\s*([a-zA-Z0-9_$.]+):')
    call_re = re.compile(r'call\s+.*@' + re.escape(target_func) + r'\b')

    for line in func_lines:
        if label_re.match(line):
            block_count += 1
        if call_re.search(line):
            found_call = True
            break
    if found_call:
        return block_count if block_count > 0 else 1
    else:
        return None  

def calc_path_blocks(path, func_bodies):
    total_blocks = 0
    if len(path) < 2:
        return 0
    for i in range(len(path)-1):
        caller = path[i]
        callee = path[i+1]
        caller_body = func_bodies.get(caller)
        if caller_body is None:
            return None
        blocks = count_blocks_between_calls(caller_body, callee)
        if blocks is None:
            return None
        total_blocks += blocks
    return total_blocks

def prune_paths_for_func(paths, ioctl_handlers, func_bodies):
    # ioctl_handler first
    ioctl_paths = []
    rest_paths = []
    for path in paths:
        if not path:
            continue
        if path[0] in ioctl_handlers:
            ioctl_paths.append(path)
        else:
            rest_paths.append(path)
    # Caluate block number for all the paths
    ioctl_blocks = []
    for p in ioctl_paths:
        b = calc_path_blocks(p, func_bodies)
        if b is not None:
            ioctl_blocks.append( (p, b) )
    ioctl_blocks.sort(key=lambda x:x[1])  # block-less first

    if len(ioctl_blocks) > 5:
        kept = [p for p, b in ioctl_blocks[:5]]
    else:
        kept = [p for p, b in ioctl_blocks]
    # Up to 3 paths
    if len(kept) < 3:
        rest_blocks = []
        for p in rest_paths:
            b = calc_path_blocks(p, func_bodies)
            if b is not None:
                rest_blocks.append( (p, b) )
        rest_blocks.sort(key=lambda x:x[1])
        for p, b in rest_blocks:
            if len(kept) >= 3:
                break
            kept.append(p)
    return kept

def main():
    if len(sys.argv) != 4:
        print("Usage: python prune_paths.py input.json ioctl.txt input.ll")
        sys.exit(1)
    infile = sys.argv[1]
    txtfile = sys.argv[2]
    llfile = sys.argv[3]

    if infile.endswith('.json'):
        outfile = infile[:-5] + '-new.json'
    else:
        outfile = infile + '-new.json'

    with open(infile, 'r', encoding='utf-8') as f:
        data = json.load(f)
    ioctl_handlers = load_ioctl_handlers(txtfile)
    func_bodies = parse_ll_functions(llfile)

    new_data = {}
    for func, paths in data.items():
        new_data[func] = prune_paths_for_func(paths, ioctl_handlers, func_bodies)

    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()