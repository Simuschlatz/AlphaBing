if __name__ == "__main__":
    import sys
    import os
    root = os.environ.get("CHEAPCHESS")
    sys.path.append(root)
    print(sys.path)

    import matplotlib as mpl
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

algs = ["minimax", "alphabeta", "optalphabeta"]
num_moves = 15
def run_benchmarks():
    bms = Manager().dict()
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

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = []
        
        for pos_id, fen in enumerate(fens):
            board = Board(fen)
            LegalMoveGenerator.init_board(board)
            futures.append(executor.submit(run_bms_for_pos, board, bms, "evaluated_nodes"))

        wait(futures)

        num_moves_skipped = sum([f.result() for f in futures])

        logger.info(fen)
        logger.info(pos_id)


    return {alg: total / (num_moves * num_positions - num_moves_skipped) for alg, total in bms.items()}


def run_bms_for_pos(board: Board, bms, mode: str):
    num_moves_skipped = 0
    for move_id in range(num_moves):

        if board.is_terminal_state(len(LegalMoveGenerator.load_moves(board))):
            num_moves_skipped += (num_moves - move_id - 1)
            break

        for alg in algs:
            val = 0
            match mode.lower():
                case "time":
                    t = perf_counter()
                    move = Dfs.search(board, algorithm=alg)
                    val = perf_counter() - t
                case "evaluated_nodes":
                    move = Dfs.search(board, algorithm=alg)
                    val = Dfs.evaluated_nodes
                case _:
                    move = Dfs.search(board, algorithm=alg)

            bms[alg] = bms.get(alg, 0) + val
            logger.info(bms[alg])

        board.make_move(move)
    return num_moves_skipped

def visualize():
    # bms = run_benchmarks()
    # coefficients, vals = zip(*bms.items())
    # coefficients = list(map(str, coefficients))
    coefficients = ['minimax', 'alphabeta', 'optalphabeta']
    vals = (1281157, 173628, 75604)
    colors = sns.color_palette("coolwarm")
    # colors = sns.cubehelix_palette(start=.5, rot=-.5)
    sorted_times = sorted(vals)
    colors = [colors[sorted_times.index(t)] for t in vals]
    
    print(coefficients, vals)
    with sns.axes_style("darkgrid"):
        plt.figure(figsize=(10, 8))
        plt.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
        plt.bar(coefficients, vals, color=colors)
        plt.title("Vergleich der Performance unterschiedlicher Suchalgorithmen", fontweight="bold")
        plt.xlabel('Algorithmus', fontweight="bold")
        plt.ylabel('Evaluierte Positionen', fontweight="bold")
    plt.show()

if __name__ == '__main__':
    visualize()
