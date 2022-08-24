class Board_utility:
    """
    Contains all methods that relate to the board but
    aren't part of the inner board representation
    """
    @staticmethod
    def get_file_and_rank(square):
        return square % 9, square // 9
    
    @staticmethod
    def get_square(file, rank):
        return rank * 9 + file
    
    @staticmethod
    def get_display_coords(file, rank, unit, off_x=0, off_y=0):
        return off_x + file * unit, off_y + rank * unit