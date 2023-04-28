if __name__ == "__main__":
    import sys
    import os
    root = os.environ.get("CHEAPCHESS")
    sys.path.append(root)
    print(sys.path)

    import matplotlib as mpl
    import numpy as np
    import matplotlib.pyplot as plt
    mpl.style.use('bmh')

    import seaborn as sns

    from concurrent.futures import ProcessPoolExecutor, wait
    from multiprocessing import Manager

    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from core.engine.ai.alphabeta import Dfs
from core.engine import Board, LegalMoveGenerator

from time import perf_counter

def run_benchmarks():
    bms = Manager().dict()
    step = 50
    max_m = 250
    num_steps = max_m // step
    num_moves = 15
    num_moves_skipped = 0
    fens = [
        "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w - - 0 1",
        "r1ea1a3/4kh3/2h1e4/pHp1p1p1p/4c4/6P2/P1P2R2P/1CcC5/9/2EAKAE2 w - - 0 1",
        "r1ea1a3/4kh3/2h1e4/pHp1p1p1p/4c4/6P2/P1P2R2P/1CcC5/9/2EAKAE2 w - - 0 1",
        "1ceak4/9/h2a5/2p1p3p/5cp2/2h2H3/6PCP/3AE4/2C6/3A1K1H1 w - - 0 1",
        "5a3/3k5/3aR4/9/5r3/5h3/9/3A1A3/5K3/2EC2E2 w - - 0 1",
        "CRH1k1e2/3ca4/4ea3/9/2hr5/9/9/4E4/4A4/4KA3 w - - 0 1",
        "R1H1k1e2/9/3aea3/9/2hr5/2E6/9/4E4/4A4/4KA3 w - - 0 1"
        ]
    num_positions = len(fens)

    for pos_id, fen in enumerate(fens):
        board = Board(fen)
        LegalMoveGenerator.init_board(board)
        logger.info(fen)
        logger.info(pos_id)
        for move_id in range(num_moves):
            if board.is_terminal_state(len(LegalMoveGenerator.load_moves(board))):
                num_moves_skipped += (num_moves - move_id - 1)
                break
            with ProcessPoolExecutor(max_workers=8) as executor:
                futures = []
                for i in range(num_steps + 1):
                    m = (step * i) or 1
                    print(m)
                    futures.append(executor.submit(run_bm, board, m, bms, "evaluated_nodes"))
            wait(futures)
            move = futures[0].result()
            board.make_move(move)

    return {m: total / (num_moves * num_positions - num_moves_skipped) for m, total in bms.items()}

def run_bm(board: Board, m, bms, mode: str):
    val = 0
    match mode.lower():
        case "time":
            t = perf_counter()
            move = Dfs.search(board, m)
            val = perf_counter() - t
        case "cutoffs":
            move = Dfs.search(board, m)
            val = Dfs.cutoffs
        case "evaluated_nodes":
            move = Dfs.search(board, m)
            val = Dfs.evaluated_nodes
        case _:
            move = Dfs.search(board, m)

    bms[m] = bms.get(m, 0) + val
    return move

def visualize():
    bms = run_benchmarks()
    coefficients, vals = zip(*sorted(bms.items(), key=lambda item: item[0], reverse=True))
    coefficients = list(map(str, coefficients))
    # coefficients = ['250', '200', '150', '100', '50', '1']
    # vals = [0.958735184755642, 0.9579678426529022, 0.9568651940227331, 0.9579102482012887, 0.9586975148245175, 1.38350047498825]
    colors = sns.color_palette("coolwarm")
    # colors = sns.cubehelix_palette(start=.5, rot=-.5)
    sorted_times = sorted(vals)
    colors = [colors[sorted_times.index(t)] for t in vals]
    
    print(coefficients, vals)
    with sns.axes_style("darkgrid"):
        plt.barh(coefficients, vals, color=colors)
        # plt.title("Vergleich der Zugsortierung-Performance mit unterschiedlichen Koeffizienten")
        plt.ylabel('Koeffizient')
        plt.xlabel('Zeit')
    plt.show()

if __name__ == '__main__':
    visualize()
