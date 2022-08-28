import numpy as np

class Zobrist_hashing:
    table = []
    lowest_value = 0
    @classmethod
    def init_table(cls):
        cls.highest_value = cls.get_largest_64_bit()
        num_sides = 2
        num_pieces = 7
        num_squares = 90
        cls.table = np.random.randint(
            cls.lowest_value, 
            cls.highest_value, 
            (num_sides, num_pieces, num_squares),
            dtype=np.int64
            )

    @staticmethod
    def get_largest_64_bit():
        num = "1" * 63
        return int(num, 2)

    @classmethod
    def get_zobrist_key(cls, moving_side, piece_lists):
        zobrist_key = 0
        for side, piece_list in enumerate(piece_lists):
            for piece_id, squares in enumerate(piece_list):
                for square in squares:
                    zobrist_key ^= cls.table[side][piece_id][square]

        zobrist_key ^= moving_side

        return zobrist_key
            
