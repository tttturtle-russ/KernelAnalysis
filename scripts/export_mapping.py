import json
import argparse
from collections import defaultdict

class ExprFuncMapper:
    def __init__(self, json_path):
        self.source2func = {}
        self.func2source = defaultdict(list)
        self.json_path = json_path

    def add(self, source_loc, func_name, func_loc):
        self.source2func[source_loc] = {
            'func_name': func_name,
            'func_loc': func_loc
        }
        self.func2source[func_name].append(source_loc)

    def save(self):
        with open(self.json_path, 'w') as f:
            json.dump({
                'source2func': self.source2func,
                'func2source': dict(self.func2source)
            }, f, indent=4)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--json_path", type=str, help="Path to the JSON file", required=True)
    argParser.add_argument("--mapping_file", type=str, help="Path to the mapping file", required=True)
    args = argParser.parse_args()
    
    mapper = ExprFuncMapper(args.json_path)
    with open(args.mapping_file, "r") as f:
        for line in f:
            source_loc, func_name, func_loc = line.strip().split("\t")
            source_loc = source_loc.strip()
            func_name = func_name.strip()
            func_loc = func_loc.strip()
            mapper.add(source_loc, func_name, func_loc)

    mapper.save()