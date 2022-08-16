from Engine.piece import Piece
from Engine.board import Board

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
      friendly_eval = cls.static_material_eval(cls.moving_side)
      opponent_eval = cls.static_material_eval(cls.opponent_side)
      return friendly_eval - opponent_eval
  
  @classmethod
  def static_material_eval(cls, side_):
      material = 0
      for piece_id in range(1, 7):
          material += len(cls.board.piece_lists[side][piece_id]) * cls.board.values[piece_id]
      return material
  def pst_material_eval(cls, side_to_move)