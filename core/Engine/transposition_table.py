from core.Engine import Zobrist_hashing, tt_entry
from core.Engine import Tt_entry

class Transposition_table:
    key_not_found = None
    exact_eval = 0
    upper_bound = 1
    lower_bound = 2
    def __init__(self, board, size=20000) -> None:
        self.board = board
        self.size = size
        self.data = [None for _ in range(self.size)]
        self.index = lambda key: key % self.size

    def del_entry(self, index):
        self.data[index] = None

    def clear(self):
        for i in range(self.size):
            self.del_entry(i)

    def look_up_eval(self, depth, alpha, beta):
        self
