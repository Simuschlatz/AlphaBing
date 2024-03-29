from core.engine.piece import Piece
from core.engine.ai.alphabeta import PieceSquareTable, Evaluation

def order_moves(moves, board, m=250):
    """
    orders moves heuristically for the best ones to be up front

    :param m: Coefficient multiplies with captured piece's value
    """
    move_value_estimates = {} # {move: value estimate, ...}
    for move in moves:
        moved_piece = board.squares[move[0]]
        captured_piece = board.squares[move[1]]
        moved_val = Evaluation.values[Piece.get_type(moved_piece)] 
        captured_val = Evaluation.values[Piece.get_type(captured_piece)]
        # Multiply captured piece value by a number higher than the most valuable piece,
        # this way good pieces capturing bad ones still overvalue non-capture moves
        move_value_estimates[move] = captured_val * m - moved_val
    # Sort move value estimates by their value and return the ordered moves
    return sorted(move_value_estimates, key=lambda move: move_value_estimates[move], reverse=True)


def order_moves_pst(moves: list[tuple], board, m=200):
    """
    orders moves heuristically based on piece-square-tables
    for the best ones to be up front

    :param m: Coefficient determining the weight of captured piece's value,
    therefore setting the level of priority for non-capture moves. The higher
    m, the lower the priority of non-capture moves.
    """
    move_values = {} # {move: value estimate, ...}
    for move in moves:
        move_from, move_to = move
        moved_piece_type = Piece.get_type(board.squares[move_from])
        captured_piece_type = Piece.get_type(board.squares[move_to])
        moved_val = PieceSquareTable.get_pst_value(moved_piece_type, move_to, board.moving_side)
        captured_val = PieceSquareTable.get_pst_value(captured_piece_type, move_to, 1 - board.moving_side)
        # Multiply captured piece value by a number higher than the most valuable pst-value,
        # this way good pieces capturing bad ones still overvalue non-capture moves
        move_values[move] = captured_val * m - moved_val
    # Sort move value estimates by their value and return the ordered moves
    return sorted(move_values, key=lambda move: move_values[move], reverse=True)
