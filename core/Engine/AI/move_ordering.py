
from Engine.piece import Piece
def order_moves(moves, board):
    """
    orders moves heuristically for the best ones to be up front
    """
    move_value_estimates = {} # {move: value estimate, ...}
    for move in moves:
        score = 0
        moved_piece = board.squares[move[0]]
        captured_piece = board.squares[move[1]]
        moved_val = board.values[Piece.get_type(moved_piece)]
        captured_val = board.values[Piece.get_type(captured_piece)]
        # Multiply captured piece value by a number higher than the most valuable piece,
        # this way good pieces capturing bad ones still overvalue non-capture moves
        score =  11 * captured_val - moved_val
        move_value_estimates[move] = score
    # Sort move value estimates by their value and return the ordered moves
    return sorted(move_value_estimates, key=lambda move: move_value_estimates[move], reverse=True)