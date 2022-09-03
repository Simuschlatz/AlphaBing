from ast import Index
import numpy as np

class Zobrist_hashing:
    """
    A neat way to generate numbers for a given state of a game, showing that sometimes 
    benefits of speed outweigh imperfection
    """
    table = []
    lowest_value = 0
    @classmethod
    def init_table(cls):
        # Set the seed to wedding anniversary of my parents for good luck :)
        np.random.seed(110697)
        cls.highest_value = cls.get_largest_64_bit()
        cls.lowest_value = -cls.highest_value
        # Create a random value for each square for each piece for each side
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
        """
        :return: does exactly what the name proposes,
        returns the largest 64-Bit number possible
        """
        # num = "1" * 64
        num = "1" * 63
        return int(num, 2)

    @classmethod
    def get_zobrist_key(cls, moving_side, piece_lists):
        """
        :return: The zobrist key for the current board
        """
        zobrist_key = 0
        # Loop over every piece side
        for side, piece_list in enumerate(piece_lists):
            # Loop over every piece list
            for piece_id, squares in enumerate(piece_list):
                # Loop over every square
                for square in squares:
                    # Xor the table value into the key
                    zobrist_key ^= cls.table[side][piece_id][square]
        zobrist_key ^= moving_side

        return zobrist_key
            
