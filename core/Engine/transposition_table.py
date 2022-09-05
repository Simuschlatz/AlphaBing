from core.Engine import Zobrist_hashing, tt_entry

class Transposition_table:
    invalid = None
    exact_eval = 0
    upper_bound = 1
    lower_bound = 2
    def __init__(self, board, size=20000) -> None:
        self.board = board
        self.size = size
        self.table = {}
        self.index = lambda key: key % self.size

    def clear(self):
        self.table.clear()

    def improve_mate_score():
        """
        improves the mate score
        """
    def look_up_eval(self, depth, alpha, beta):
        key = self.board.zobrist_key
        index = self.index(key)
        entry = self.table.get(index, None)
        if entry:
            if key != entry.key:
                return self.invalid
            if depth > entry.depth:
                return self.invalid
            if entry.type == self.exact_eval:
                return entry.score
            if entry.type == self.upper_bound and entry.score <= alpha:
                return entry.score
            if entry.type == self.lower_bound and entry.score >= beta:
                return entry.score
        return self.invalid


