import time
from Engine.move_generator import Legal_move_generator

b = None
def b_to_the_d(depth):
    moves = Legal_move_generator.load_moves()
    num_positions = 0
    if not depth - 1:
        num_positions += len(moves)
        return num_positions
    for move in moves:
        b.make_move(move)
        num_positions += b_to_the_d(depth - 1)
        b.reverse_move()
    return num_positions

def get_num_positions(depth, board):
    global b
    b = board
    p_t = time.perf_counter()
    num_positions = b_to_the_d(depth)
    print(f"depth: {depth} || nodes searched: {num_positions} || time: {time.perf_counter() - p_t}")
