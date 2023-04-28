import numpy as np

class ZobristHashing:
    """
    A neat way to generate n-bit binaries for a given position, 
    showing that sometimes benefits of speed outweigh imperfection (rare hash collisions)
    """
    lowest_value = 0
    
    ### Didn't put this in a class function because it would have had to be called in every child process
    ### leading toa lot of redudancy

    # Set the seed to wedding anniversary of my parents for good luck :)
    # np.random.seed(110697) # Had to take this out for uniqueness of multiprocess training pipeline
    largest_64 = "1" * 63
    highest_value = int(largest_64, 2)
    lowest_value = -highest_value
    # Create a random value for each square for each piece for each side
    num_sides = 2
    num_pieces = 7
    num_squares = 90

    table = np.random.randint(
        lowest_value, 
        highest_value, 
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
    def digest(cls, moving_side: int, piece_lists: list):
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
            
