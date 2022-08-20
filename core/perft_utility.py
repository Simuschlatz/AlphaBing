import time
from Engine.move_generator import Legal_move_generator
from Engine.board import Board

board = Board("rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR", 1)
Legal_move_generator.init_board(board)
captures = 0

def dfs(depth):
    moves = Legal_move_generator.load_moves()
    num_positions = 0
    if not depth - 1:
        num_positions += len(moves)
        return num_positions
    for move in moves:
        board.make_move(move)
        num_positions += dfs(depth - 1)
        board.reverse_move()

    return num_positions

depth = 4
p_t = time.perf_counter()
num_positions = dfs(depth)
print(f"depth: {depth} || nodes searched: {num_positions} || time: {time.perf_counter() - p_t}")
