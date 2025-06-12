import os
import re
import json
import sys

def parse_path_point(point):
    # Parse a path point string like "/path/to/file.c:123  funcname"
    m = re.match(r'(.+):(\d+)\s+(\S+)$', point)
    if not m:
        raise ValueError(f"Bad format: {point}")
    filename, lineno, funcname = m.group(1), int(m.group(2)), m.group(3)
    return filename, lineno, funcname

def extract_code_segment(filename, start_line, next_funcname=None, end_line=None):
    """
    Extract code from filename, starting at start_line:
    - If next_funcname is given (not at the terminal path point), extract up to (and including) the first call to next_funcname.
    - If end_line is given (for the terminal path point), extract from start_line up to and including end_line.
    - All lines are joined with tab instead of real newlines.
    - The filename is prefixed with $TOP_DIR/../ if $TOP_DIR is set.
    """
    top_dir = os.environ.get('MY_PATH', '').rstrip('/')
    print("top_dir is: " + top_dir)
    if top_dir:
        rel_filename = os.path.relpath(filename, '/')
        print("rel_filename is: " + rel_filename)
        real_path = os.path.normpath(os.path.join(top_dir, rel_filename))
    else:
        real_path = filename
    print("real_path is: " + real_path)
    
    try:
        with open(real_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return f"<Error opening file {real_path}: {e}>"

    idx = start_line - 1  # Convert to 0-based index
    if idx < 0 or idx >= len(lines):
        return "<Line out of range>"
    segment = []

    # Case 1: Not the terminal node, extract up to call of next_funcname
    if next_funcname and not end_line:
        for i in range(idx, len(lines)):
            segment.append(lines[i].rstrip('\n'))
            call_pat = r'\b{}\s*\('.format(re.escape(next_funcname))
            if re.search(call_pat, lines[i]):
                break
        return '\t'.join(segment)
    # Case 2: Terminal node, extract from start_line up to and including end_line
    elif end_line:
        for i in range(idx, min(end_line, len(lines))):
            segment.append(lines[i].rstrip('\n'))
        return '\t'.join(segment)
    else:
        # Fallback: just return the start line
        return lines[idx].rstrip('\n')

def main():
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} input.json output.json number1 number2")
        sys.exit(1)

    input_json = sys.argv[1]
    output_json = sys.argv[2]
    number1 = int(sys.argv[3])
    number2 = int(sys.argv[4])

    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    keys = list(data.keys())
    if len(keys) != 2:
        print("Error: Input JSON must contain exactly two top-level keys.")
        sys.exit(2)

    # Map each top-level key to its corresponding terminal end line
    key_numbers = {keys[0]: number1, keys[1]: number2}

    new_data = {}
    for key in keys:
        end_number = key_numbers[key]
        new_paths = []
        for path in data[key]:
            code_path = []
            for i, point in enumerate(path):
                filename, lineno, funcname = parse_path_point(point)
                # If this is the last point in the path
                if i == len(path) - 1:
                    code_segment = extract_code_segment(filename, lineno, end_line=end_number)
                else:
                    # Not terminal, extract up to next function call
                    next_funcname = None
                    if i + 1 < len(path):
                        _, _, next_funcname = parse_path_point(path[i+1])
                    code_segment = extract_code_segment(filename, lineno, next_funcname=next_funcname)
                # Prepend the original path point and the separator
                code_path.append(point + ' ||| ' + code_segment)
            new_paths.append(code_path)
        new_data[key] = new_paths

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()