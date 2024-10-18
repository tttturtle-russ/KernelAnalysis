class Instruction:
    def __init__(self) -> None:
        self.write_to = set()
        self.read_from = set()
        self.source_loc = None

    """Read a line from SVF output and parse it into useful values

    readline only handles the following situations:
    1. LDMU: reprents the instruction reads from memory
    2. STCHI: reprents the instruction writes to memory
    3. source loc: parse the source location of the instrcution
    """
    def readline(self,line: str) -> None:
        pts = self.__parse_pts(line)
        if "LDMU" in line:
            self.read_from = self.read_from.union(pts)
        elif "STCHI" in line:
            self.write_to = self.write_to.union(pts)
        elif "{" in line:
            self.source_loc = self.__parse_source_loc(line)


    @staticmethod
    def __parse_pts(line: str) -> set:
        pts = line[line.index('{'):line.index('}')]
        return set(map(int, pts.split()))
    
    @staticmethod
    def __parse_source_loc(line:str) -> str:
        ...

class MemPairs:
    def __init__(self) -> None:
        self.pairs = {}

    def add_pair(self,):
        ...
