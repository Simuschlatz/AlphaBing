class Piece:
    """Pieces' values are declared in way where they can also be
    used for indexnig in list of images"""
    king = 0
    elephant = 1
    advisor = 2
    cannon = 3
    pawn = 4
    rook = 5
    horse = 6
    black = 0
    red = 1
    letters = "keacprhKEACPRH"

    @staticmethod
    def is_color(piece, color):
        # piece is equal to 0 when target_square is empty so piece[0] would raise TypeError
        if not piece: 
            return False
        return piece[0] == color
    
    @staticmethod
    def is_type(piece, piece_type):
        if not piece: 
            return False
        return piece[1] == piece_type