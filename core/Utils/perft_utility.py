"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
from core.Engine.move_generator import Legal_move_generator

def get_perft_result(depth, board):
    """
    A performance test for move generation algorithms by calculating the number
    of board configurations found for a given number of moves in the future
    :return: The branching factor b to the power of depth d, in other words:
    The total number of possible positions found looking depth moves ahead
    """
    moves = Legal_move_generator.load_moves()
    num_positions = 0
    if not depth - 1:
        num_positions += len(moves)
        return num_positions
    for move in moves:
        board.make_move(move)
        num_positions += get_perft_result(depth - 1, board)
        board.reverse_move()
    return num_positions
