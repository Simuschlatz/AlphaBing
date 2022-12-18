"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from core.Engine import ZobristHashing, TtEntry

class TranspositionTable:
    """
    TODO: repetition
    """
    invalid = None
    exact_eval = 0
    upper_bound = 1
    lower_bound = 2

    key = 0
    depth = 1
    type = 2
    eval = 3
    move = 4
    def __init__(self, board, size=20000) -> None:
        self.board = board
        self.size = size
        self.table = {}
        self.index = lambda key: key % self.size

    def clear(self):
        self.table.clear()

    def improve_mate_score():
        pass
    
    def store_pos(self, depth, eval, node_type, move):
        key = self.board.zobrist_key
        index = self.index(key)
        entry = [key, depth, node_type, eval, move]
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

    def get_move(self):
        return self.table[self.index(self.board.zobrist_key)][self.move]

