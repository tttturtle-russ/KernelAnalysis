import json
import itertools
import argparse

class Instruction:
    def __init__(self) -> None:
        self.write_to = set()
        self.read_from = set()
        self.source_loc = None
        self.is_write = None

    """Read a line from SVF output and parse it into useful values

    readline only handles the following situations:
    1. LDMU: reprents the instruction reads from memory
    2. STCHI: reprents the instruction writes to memory
    3. source loc: parse the source location of the instrcution

    Args:
        line: one line from SVF output

    Return:
        bool: if the instruction has beem constructed
    """
    def readline(self,line: str) -> bool:
        if "LDMU" in line:
            pts = self.__parse_pts(line)
            self.read_from = self.read_from.union(pts)
            self.is_write = False
        elif "STCHI" in line:
            pts = self.__parse_pts(line)
            self.write_to = self.write_to.union(pts)
            self.is_write = True
        elif "SourceLoc" in line:
            self.source_loc = self.__parse_source_loc(line.split("->")[1])
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
    def __parse_pts(line: str) -> set:
        pts = line[line.index('{')+1:line.index('}')].strip()
        return set(map(int, pts.split()))
    
    @staticmethod
    def __parse_source_loc(line:str) -> str:
        loc = json.loads(line.strip())
        return f"{loc["fl"]}:{loc["ln"]}"

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
        write_write = list(itertools.product(self.write_insts, self.write_insts))
        write_read = list(itertools.product(self.write_insts, self.read_insts))
        result = set()

        for w1,w2 in write_write:
            result.add(f"{w1}->W {w2}->W")

        for w,r in write_read:
            result.add(f"{w}->W {r}->R")

        return list(result)

class MemPairs:
    def __init__(self) -> None:
        self.pairs = []

    def add_pair(self, pair: str):
        self.pairs.append(pair)

    def dump(self):
        for pair in self.pairs:
            print(pair)

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument("mssa")
    args = argParser.parse_args()
    memory_locations = {}
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
                
                inst.reset()

        result = MemPairs()
        for memory, loc in memory_locations.items():
            for mempair in loc.generate_mempair():
                result.add_pair(mempair)

        result.dump()
