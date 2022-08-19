from Engine.piece import Piece
from Engine.AI.piece_square_tables import get_pst_value
def order_moves(moves, board):
    """
    orders moves heuristically for the best ones to be up front
    """
    move_value_estimates = {} # {move: value estimate, ...}
    for move in moves:
        moved_piece = board.squares[move[0]]
        captured_piece = board.squares[move[1]]
        moved_val = board.values[Piece.get_type(moved_piece)] 
        captured_val = board.values[Piece.get_type(captured_piece)]
        # Multiply captured piece value by a number higher than the most valuable piece,
        # this way good pieces capturing bad ones still overvalue non-capture moves
        move_value_estimates[move] = 250 * captured_val - moved_val
    # Sort move value estimates by their value and return the ordered moves
    return sorted(move_value_estimates, key=lambda move: move_value_estimates[move], reverse=True)

def order_moves_pst(moves, board):
    """
    orders moves heuristically based on piece-square-tables
    for the best ones to be up front
    """
    move_value_estimates = {} # {move: value estimate, ...}
    for move in moves:
        move_from, move_to = move
        is_board_flipped = board.moving_side == Piece.red != board.is_red_up
        summand = 89 * is_board_flipped
        square_multiplier = 2 * (not is_board_flipped) - 1
        moved_val = get_pst_value(Piece.get_type(board.squares[move_from]), summand + square_multiplier * move_from)
        captured_piece = board.squares[move_to]
        if captured_piece:
            summand = 89 - summand
            square_multiplier = 2 * (is_board_flipped) - 1
            captured_val = get_pst_value(Piece.get_type(captured_piece), summand + square_multiplier * move_to)
        else:
            captured_val = 0
        # Multiply captured piece value by a number higher than the most valuable pst-value,
        # this way good pieces capturing bad ones still overvalue non-capture moves
        move_value_estimates[move] = captured_val * 250 - moved_val
    # Sort move value estimates by their value and return the ordered moves
    return sorted(move_value_estimates, key=lambda move: move_value_estimates[move], reverse=True)
