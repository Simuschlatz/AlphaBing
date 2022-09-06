from core.Engine import Zobrist_hashing, tt_entry

class Transposition_table:
    invalid = None
    exact_eval = 0
    upper_bound = 1
    lower_bound = 2

    key = 0
    depth = 1
    type = 2
    eval = 3

    def __init__(self, board, size=20000) -> None:
        self.board = board
        self.size = size
        self.table = {}
        self.index = lambda key: key % self.size

    def clear(self):
        self.table.clear()

    def improve_mate_score():
        pass
    
    def store_pos(self, depth, eval, node_type):
        key = self.board.zobrist_key
        index = self.index(key)
        entry = [key, depth, node_type, eval]
        self.table[index] = entry

    def look_up_eval(self, depth, alpha, beta):
        key = self.board.zobrist_key
        index = self.index(key)
        entry = self.table.get(index, None)
        if entry:
            if key != entry[self.key]:
                return self.invalid

            if depth > entry[self.depth]:
                return self.invalid

            if entry[self.type] == self.exact_eval:
                return entry[self.eval]
            if entry[self.type] == self.upper_bound and entry[self.eval] <= alpha:
                return entry[self.eval]
            if entry[self.type] == self.lower_bound and entry[self.eval] >= beta:
                return entry[self.eval]

        return self.invalid


