from core.engine import LegalMoveGenerator, Board
from time import perf_counter
from logging import getLogger
logger = getLogger(__name__)

def start_search(board: Board):
    depth = str()
    while True:
        depth = input("Enter search depth: ")
        if not depth.isdigit():
            continue
        depth = int(depth)
        if depth > 0:
            break
    logger.info("starting perft search... This might take some time")
    iterative = False
    depths = [depth]
    if iterative:
        depths = range(1, depth + 1)
    for d in depths:
        get_num_positions(d, board)

def get_perft_result(depth: int, board: Board):
    """
    A performance test for move generation algorithms by calculating the number
    of board configurations found for a given number of moves in the future
    :return: The branching factor b to the power of depth d, in other words:
    The total number of possible positions found looking depth moves ahead
    """
    moves = LegalMoveGenerator.load_moves()
    num_positions = 0
    if not depth - 1:
        num_positions += len(moves)
        return num_positions
    for move in moves:
        board.make_move(move, search_state=True)
        num_positions += get_perft_result(depth - 1, board)
        board.reverse_move(search_state=True)
    return num_positions

def multiprocess_perft(depth: int, board: Board):
    moves = LegalMoveGenerator.load_moves()
    num_positions = 0
    if not depth - 1:
        num_positions += len(moves)
        return num_positions
    for move in moves:
        board.make_move(move, search_state=True)
        num_positions += get_perft_result(depth - 1, board)
        board.reverse_move(search_state=True)
    return num_positions

def get_num_positions(depth: int, board: Board):
    p_t = perf_counter()
    num_positions = get_perft_result(depth, board)
    time = perf_counter() - p_t
    logger.info(f"depth: {depth} || nodes searched: {num_positions} || time: {round(time, 2)}")

    