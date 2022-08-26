import numpy as np

class Zobrist_hashing:
    table = []
    lowest_value = 0
    highest_value = 2147483647
    @classmethod
    def init_table(cls):
        cls.table = np.random.randint(cls.lowest_value, cls.highest_value, (2, 7, 90))

    @classmethod
    def get_zobrist_key(cls, moving_side, piece_lists):
        zobrist_key = 0
        for piece_id, squares in enumerate(piece_lists):
            for square in squares:
                zobrist_key ^= cls.table[moving_side][piece_id][square]
        
        return zobrist_key
        
                


Zobrist_hashing.init_table()
                


