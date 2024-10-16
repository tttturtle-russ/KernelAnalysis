class Instruction:
    def __init__(self) -> None:
        self.write_to = {}
        self.read_from = {}

    """Read a line from SVF output and parse it into useful values

    readline only handles the following situations:
    1. 
    """
    def readline(line: str) -> None:
        ...