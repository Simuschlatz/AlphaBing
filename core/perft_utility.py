from move_generator import Legal_move_generator
from board import Board
board = Board("RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr", 1)
m_g = Legal_move_generator(board)

def dfs(depth):
    if depth == 0:
        return 1
    moves = m_g.load_moves()
    num_positions = 0

    for move in moves:
        board.make_move(move)
        num_positions += dfs(depth - 1)
        board.reverse_move()

    return num_positions

# for depth in range(1, 4):
depth = 4
num_positions = dfs(depth)
print(f"depth: {depth} positions: {num_positions}")