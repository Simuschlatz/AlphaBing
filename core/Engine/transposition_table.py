from core.Engine import Zobrist_hashing, tt_entry
from core.Engine import Tt_entry

class Transposition_table:
    def __init__(self, board, size=10000) -> None:
        self.board = board
        self.size = size
        self.data = {}
    
    def store_eval(self, alpha, beta, plies_from_root, eval):
        entry = tt_entry
