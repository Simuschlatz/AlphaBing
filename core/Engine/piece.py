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
    black = 8
    red = 16
    letters = "keacprhKEACPRH"

    @staticmethod
    def is_color(piece, color):
        return piece & 0b11000 == color
    
    @staticmethod
    def is_type(piece, typ):
        return piece & 0b00111 == typ

    @staticmethod
    def is_piece(piece, color, typ):
        return piece == color + typ

    @staticmethod
    def get_color(piece):
        return piece & 0b11000
    
    @staticmethod
    def get_type(piece):
        return piece & 0b00111