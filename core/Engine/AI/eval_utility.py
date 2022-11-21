"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
from core.Engine.AI.piece_square_tables import PieceSquareTable

class Evaluation:
    # Piece's values
    king = float("inf")
    pawn = 10
    advisor = 20
    elephant = 20
    horse = 40
    cannon = 45
    rook = 100
    values = (0, elephant, advisor, cannon, pawn, rook, horse)

    @classmethod
    def init(cls, board):
        cls.board = board

    @classmethod
    def shef(cls):
        """
        Standard Heuristic Evaluation Function \n
        :return: a heuristic evaluation of current material on board relative to moving color.
        positive: good
        negative: bad
        """
        friendly_eval = cls.static_material_eval(cls.board.moving_color)
        opponent_eval = cls.static_material_eval(cls.board.opponent_color)
        return friendly_eval - opponent_eval

    @classmethod
    def static_material_eval(cls, moving_color):
        mat = 0
        for piece_id in range(1, 7):
            mat += len(cls.board.piece_lists[moving_color][piece_id]) * cls.values[piece_id]
        return mat

    @classmethod
    def pst_shef(cls):
        """
        Advanced Standard Heuristic Evaluation Function \n
        :return: a heuristic piece-square-table-based evaluation of current material on board relative to moving color.
        """
        friendly_eval = cls.pst_material_eval(cls.board.moving_color)
        opponent_eval = cls.pst_material_eval(cls.board.opponent_color)
        return friendly_eval - opponent_eval

    @classmethod  
    def pst_material_eval(cls, moving_side):
        """
        :return: Piece-square-table-based evaluation of moving side's material
        """
        mat = 0
        for piece_id in range(1, 7):
            for square in cls.board.piece_lists[moving_side][piece_id]:
                mat += PieceSquareTable.get_pst_value(piece_id, square, moving_side)
        return mat


      

