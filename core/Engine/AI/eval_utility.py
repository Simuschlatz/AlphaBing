from Engine.piece import Piece
from Engine.AI.piece_square_tables import piece_square_tables

class Evaluation:

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
        friendly_eval = cls.static_material_eval(cls.board.moving_side)
        opponent_eval = cls.static_material_eval(cls.board.opponent_side)
        return friendly_eval - opponent_eval

    @classmethod
    def static_material_eval(cls, moving_side):
        mat = 0
        for piece_id in range(1, 7):
            mat += len(cls.board.piece_lists[moving_side][piece_id]) * cls.board.values[piece_id]
        return mat

    @classmethod
    def shef_advanced(cls):
        is_board_flipped = cls.board.moving_side == Piece.red != cls.board.is_red_up
        summand = 89 * is_board_flipped
        square_multiplier = 2 * (not is_board_flipped) - 1
        friendly_eval = cls.pst_material_eval(cls.board.moving_side, summand, square_multiplier)
        
        square_multiplier = 2 * (is_board_flipped) - 1
        opponent_eval = cls.pst_material_eval(cls.board.opponent_side, 89 - summand, square_multiplier)
        return friendly_eval - opponent_eval

    @classmethod  
    def pst_material_eval(cls, moving_side, summand, square_multiplier):
        """
        :param summand: either 0 or 89
        :param square_multiplier: gets multiplied with the square index of each piece and then added to summand
        """
        mat = 0
        for piece_id in range(1, 7):
            for square in cls.board.piece_lists[moving_side][piece_id]:
            # Subtract 1 from piece id because piece-square-tables do not include king values
                pst = piece_square_tables[piece_id - 1]
                mat += pst[summand + square_multiplier * square]
        return mat


      

