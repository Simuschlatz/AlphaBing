import time
from Engine.move_generator import Legal_move_generator
from Engine.board import Board

board = Board("RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr", 1)

def dfs(depth):
    moves = Legal_move_generator.load_moves(board)
    num_positions = 0
    if not depth - 1:
        num_positions += len(moves)
        return num_positions
    for move in moves:
        board.make_move(move)
        num_positions += dfs(depth - 1)
        board.reverse_move()

    return num_positions

# for depth in range(1, 4):
depth = 3
p_t = time.perf_counter()
num_positions = dfs(depth)
print(f"depth: {depth} || nodes: {num_positions} || time: {time.perf_counter() - p_t}")
