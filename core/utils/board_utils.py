class BoardUtility:
    """
    Contains all methods that relate to the board but
    aren't part of the inner board representation
    """
    @staticmethod
    def get_board_pos(mouse_pos: tuple, unit: int, off_x=0, off_y=0) -> tuple:
        mouse_x = mouse_pos[0] - off_x
        mouse_y = mouse_pos[1] - off_y
        rank = int((mouse_y) // unit)
        file = int((mouse_x) // unit)
        # clamping return value within the dimensions of the board
        rank = min(9, max(rank, 0))
        file = min(8, max(file, 0))
        return file, rank
        
    @staticmethod
    def get_display_coords(file: int, rank: int, unit: int, off_x=0, off_y=0):
        return off_x + file * unit, off_y + rank * unit
    
    @staticmethod
    def get_inital_fen(play_as_red: bool, move_first: bool):
        red_moves_first = play_as_red == move_first
        INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
        INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"
        fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN 
        fen += (" w " if red_moves_first else " b ") + "- - 0 1"
        return fen