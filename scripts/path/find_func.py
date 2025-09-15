import sys

def parse_tags(tags_file):
    funcs = []
    with open(tags_file) as f:
        for line in f:
            cols = line.split()
            if len(cols) >= 4 and cols[1] == 'function':
                # cols[0]: 函数名, cols[2]: 行号, cols[3]: 文件名
                funcs.append((int(cols[2]), cols[0]))
    funcs.sort()
    return funcs

def find_func(funcs, lineno):
    result = None
    for i, (start, name) in enumerate(funcs):
        end = funcs[i+1][0] if i+1 < len(funcs) else float('inf')
        if start <= lineno < end:
            result = name
            break
    return result

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 find_func.py <tags_file> <lineno>")
        sys.exit(1)
    tags_file = sys.argv[1]
    lineno = int(sys.argv[2])
    funcs = parse_tags(tags_file)
    result = find_func(funcs, lineno)
    if result:
        print(result)
    else:
        print("Not found")
        sys.exit(2)