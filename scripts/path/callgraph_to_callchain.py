import sys
import re
import json
from collections import defaultdict

def normalize_func_name(name):
    # 去掉 .数字 后缀
    return re.sub(r'\.\d+$', '', name)

def parse_dot(dot_file):
    addr_to_name = {}
    child_to_parents = defaultdict(set)
    node_re = re.compile(r'(?P<addr>Node0x[0-9a-f]+) \[shape=record,label="\{(?P<name>[^}]*)\}"\];')
    edge_re = re.compile(r'(?P<parent>Node0x[0-9a-f]+) -> (?P<child>Node0x[0-9a-f]+);')
    with open(dot_file, 'r') as f:
        for line in f:
            node_m = node_re.match(line.strip())
            if node_m:
                # 归一化函数名
                addr_to_name[node_m.group('addr')] = normalize_func_name(node_m.group('name'))
            else:
                edge_m = edge_re.match(line.strip())
                if edge_m:
                    parent = edge_m.group('parent')
                    child = edge_m.group('child')
                    child_to_parents[child].add(parent)
    return addr_to_name, child_to_parents

def find_func_addr(addr_to_name, func_name):
    # 归一化目标函数名
    norm_func_name = normalize_func_name(func_name)
    for addr, name in addr_to_name.items():
        if name == norm_func_name:
            return addr
    return None

def reverse_paths(child_to_parents, start_addr):
    paths = []
    stack = [([start_addr], start_addr)]
    while stack:
        path, node = stack.pop()
        parents = child_to_parents.get(node, set())
        if not parents:
            paths.append(list(reversed(path)))
        else:
            for parent in parents:
                if parent not in path:
                    stack.append((path + [parent], parent))
    return paths

def addr_path_to_name_path(paths, addr_to_name):
    name_paths = []
    for addr_path in paths:
        names = [addr_to_name.get(addr, addr) for addr in addr_path]
        name_paths.append(names)
    return name_paths

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py built-in.bc.callgraph.dot function_name output.json")
        sys.exit(1)
    dot_file = sys.argv[1]
    func_name = sys.argv[2]
    output_json = sys.argv[3]

    addr_to_name, child_to_parents = parse_dot(dot_file)
    func_addr = find_func_addr(addr_to_name, func_name)
    
    if not func_addr:
        print(f"Function node for {func_name} not found in .dot file!")
        sys.exit(2)
    
    paths = reverse_paths(child_to_parents, func_addr)
    name_paths = addr_path_to_name_path(paths, addr_to_name)
    
    # 归一化 key
    norm_func_name = normalize_func_name(func_name)
    if all(len(p) == 1 and p[0] == norm_func_name for p in name_paths):
        print(f"Note: {norm_func_name} is never called by any other function (root or isolated).")
    
    result = {norm_func_name: name_paths}
    with open(output_json, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Saved call chains for {norm_func_name} to {output_json}")