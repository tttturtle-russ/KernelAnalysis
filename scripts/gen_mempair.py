import json
import itertools
import argparse

class Instruction:
    def __init__(self) -> None:
        self.write_to = set()
        self.read_from = set()
        self.source_loc = None
        self.is_write = None
        self.func = None

    """Read a line from SVF output and parse it into useful values

    readline only handles the following situations:
    1. LDMU: the instruction reads from memory
    2. CALMU: the instruction calls a function that reads from memory
    3. STCHI: the instruction writes to memory
    4. CALCHI: the instruction calls a function that writes to memory
    5. SourceLoc: parse the source location of the instruction

    Args:
        line: one line from SVF output

    Return:
        bool: if the instruction has beem constructed
    """
    def readline(self, line: str) -> bool:
        if "LDMU" in line or "CALMU" in line:
            pts = self.__parse_pts(line)
            self.read_from = self.read_from.union(pts)
            self.is_write = False
        elif "STCHI" in line or 'CALCHI' in line:
            pts = self.__parse_pts(line)
            self.write_to = self.write_to.union(pts)
            self.is_write = True
        elif "SourceLoc" in line:
            self.source_loc = self.__parse_source_loc(line.split("->")[1])
        elif "FunctionLoc" in line:
            self.func = self.__parse_function(line.split("->")[1])
            return True
    
        return False

    def memory_access(self) -> list:
        return list(zip(self.write_to, [True]*len(self.write_to))) + \
                list(zip(self.read_from, [False]*len(self.read_from)))

    def reset(self) -> None:
        self.write_to.clear()
        self.read_from.clear()
        self.is_write = None
        self.source_loc = None

    @staticmethod
    def __parse_function(line: str) -> str:
        loc = json.loads(line.strip())
        return f"{loc["file"]}:{loc["ln"]}"

    @staticmethod
    def __parse_pts(line: str) -> set:
        pts = line[line.index('{')+1:line.index('}')].strip()
        return set(map(int, pts.split()))
    
    @staticmethod
    def __parse_source_loc(line:str) -> str:
        loc = json.loads(line.strip())
        return f"{loc["fl"]}:{loc["ln"]}"

class FunctionMapping:
    def __init__(self) -> None:
        self.mapping = {}

    def add_instruction(self, inst: Instruction) -> None:
        if inst.source_loc not in self.mapping:
            self.mapping[inst.source_loc] = set()
        self.mapping[inst.source_loc].add(inst.func)

    def dump2file(self, path):
        with open(path, "a") as f:
            for source, funcs in self.mapping.items():
                f.write(f"{source}:{funcs}\n")


class MemoryLoc:
    def __init__(self) -> None:
        self.read_insts = set()
        self.write_insts = set()

    def add_instruction(self, inst: Instruction) -> None:
        if inst.is_write:
            self.write_insts.add(inst.source_loc)
        else:
            self.read_insts.add(inst.source_loc)

    def generate_mempair(self) -> set:
        # write_write = list(itertools.product(self.write_insts, self.write_insts))
        write_write = {tuple(sorted((w1, w2))) for w1, w2 in itertools.product(self.write_insts, repeat=2)}
        write_read = list(itertools.product(self.write_insts, self.read_insts))
        result = set()

        for w1,w2 in write_write:
            result.add(f"{w1}->W {w2}->W")

        for w,r in write_read:
            result.add(f"{w}->W {r}->R")

        return result

class MemPairs:
    def __init__(self) -> None:
        self.pairs = []

    def add_pair(self, pair: str):
        self.pairs.append(pair)

    def dump2file(self, file):
        with open(file, "a") as f:
            for pair in self.pairs:
                f.write(f"{pair}\n")

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument("mssa")
    argParser.add_argument("mempair")
    argParser.add_argument("source2func")
    args = argParser.parse_args()
    memory_locations = {}
    mapping = FunctionMapping()
    with open(args.mssa, "r") as mssa:
        inst = Instruction()
        for line in mssa:
            is_finished = inst.readline(line)
            if is_finished:
                for memory, is_write in inst.memory_access():
                    if memory == 1:
                        continue # don't know why but let's just skip this
                    if memory not in memory_locations:
                        memory_locations[memory] = MemoryLoc()
                    memory_locations[memory].add_instruction(inst)
                mapping.add_instruction(inst)
                inst.reset()

        result = MemPairs()
        for memory, loc in memory_locations.items():
            for mempair in loc.generate_mempair():
                result.add_pair(mempair)

        mapping.dump2file(args.source2func)
        result.dump2file(args.mempair)
