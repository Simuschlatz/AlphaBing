def order_moves(moves, board):
    """
    orders moves heuristically for the best ones to be up front
    """
    move_value_estimates = {}
    for move in moves:
        score = 0
        moved_piece = board.squares[move[0]]
        captured_piece = board.squares[move[1]]
        moved_val = board.values[moved_piece & 0b00111]
        captured_val = board.values[captured_piece & 0b00111]
        score = captured_val - moved_val
        move_value_estimates[move] = score
    return sorted(move_value_estimates)
    
    