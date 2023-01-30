"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from core.engine.AI.ABMM.piece_square_tables import PieceSquareTable
from core.engine.board import Board

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

    @staticmethod
    def pst_shef(board: Board):
        """
        Advanced Standard Heuristic Evaluation Function \n
        :return: a heuristic piece-square-table-based evaluation of current material on board relative to moving color.
        """
        friendly_eval = Evaluation.pst_material_eval(board.moving_color, board)
        opponent_eval = Evaluation.pst_material_eval(board.opponent_color, board)
        return friendly_eval - opponent_eval

    @staticmethod  
    def pst_material_eval(moving_side, board):
        """
        :return: Piece-square-table-based evaluation of moving side's material
        """
        mat = 0
        for piece_id in range(1, 7):
            for square in board.piece_lists[moving_side][piece_id]:
                mat += PieceSquareTable.get_pst_value(piece_id, square, moving_side)
        return mat
        
    @classmethod
    def shef(cls, board: Board):
        """
        Standard Heuristic Evaluation Function \n
        :return: a heuristic evaluation of current material on board relative to moving color.
        positive: good
        negative: bad
        """
        friendly_eval = cls.static_material_eval(board)
        opponent_eval = cls.static_material_eval(board)
        return friendly_eval - opponent_eval

    @staticmethod
    def static_material_eval(board: Board):
        mat = 0
        for piece_id in range(1, 7):
            mat += len(board.piece_lists[board.moving_color][piece_id]) * Evaluation.values[piece_id]
        return mat



      

