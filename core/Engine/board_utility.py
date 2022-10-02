"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
class Board_utility:
    """
    Contains all methods that relate to the board but
    aren't part of the inner board representation
    """
    @staticmethod
    def get_board_pos(mouse_pos, unit, off_x=0, off_y=0) -> tuple:
        mouse_x = mouse_pos[0] - off_x
        mouse_y = mouse_pos[1] - off_y
        rank = int((mouse_y) // unit)
        file = int((mouse_x) // unit)
        # clamping return value within the dimensions of the board
        rank = min(9, max(rank, 0))
        file = min(8, max(file, 0))
        return file, rank

    @staticmethod
    def get_file_and_rank(square):
        return square % 9, square // 9
    
    @staticmethod
    def get_square(file, rank):
        return rank * 9 + file

    @staticmethod
    def get_display_coords(file, rank, unit, off_x=0, off_y=0):
        return off_x + file * unit, off_y + rank * unit
    
    