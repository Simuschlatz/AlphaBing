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
    colors = "bw"
    @staticmethod
    def get_color(piece: tuple[int, int]):
        if not piece:
            return False
        return piece[0]
    
    @staticmethod
    def get_color_no_check(piece: tuple[int, int]):
        return piece[0]

    @staticmethod
    def get_type(piece: tuple[int, int]):
        if not piece:
            return False
        return piece[1]

    @staticmethod
    def get_type_no_check(piece: tuple[int, int]):
        return piece[1]

    @staticmethod
    def is_color(piece, color):
        if not piece:
            return False
        return piece[0] == color
    
    @staticmethod
    def is_type(piece, piece_type):
        if not piece: 
            return False
        return piece[1] == piece_type

    @staticmethod
    def is_color_no_check(piece, color):
        return piece[0] == color

    @staticmethod
    def is_type_no_check(piece, piece_type):
        return piece[1] == piece_type

    @staticmethod
    def is_piece(piece, color, type):
        return (color, type) == piece
