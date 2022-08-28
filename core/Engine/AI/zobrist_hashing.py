import numpy as np

class Zobrist_hashing:
    table = []
    lowest_value = 0
    @classmethod
    def init_table(cls):
        cls.highest_value = cls.get_largest_64_bit()
        cls.table = np.random.randint(cls.lowest_value, cls.highest_value, (2, 7, 90))

    @staticmethod
    def get_largest_64_bit():
        num = "0b" + "1" * 63
        return int(num, 2)

    @classmethod
    def get_zobrist_key(cls, moving_side, piece_lists):
        zobrist_key = 0
        for piece_id, squares in reversed(enumerate(piece_lists)):
            for square in squares:
                zobrist_key ^= cls.table[moving_side][piece_id][square]
        
        return zobrist_key
                

Zobrist_hashing.init_table()
