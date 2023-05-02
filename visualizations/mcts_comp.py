if __name__ == "__main__":
    import sys
    import os
    root = os.environ.get("CHEAPCHESS")
    sys.path.append(root)
    print(sys.path)

    import numpy as np
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from pickle import Unpickler
    import multiprocessing as mp
    import pandas as pd

from core.utils import save_time_benchmark, BoardUtility
from core.engine import Board, LegalMoveGenerator

from core.engine.ai.selfplay_rl import MCTS, CNN
from core.engine.ai.selfplay_rl.MCTS import OldMCTS
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fen = BoardUtility.get_inital_fen(True, True)

def play(num_sims=40):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data. Form: (s, π) where s is the state represented as set of bitboards, 
        π is the probability  distribution returned by MCTS. When a terminal state is reached, each 
        training example is extended by the outcome z of that game from the sample's side's perspective.

        Final Form of each example: (s, π, z)
        
        This function can be run in parallel (on multiple processes). In each process, it loads the
        tensorflow graph and starts a separate session.
        """
        board = Board(fen)
        print(fen)
        # Initialize the current tf graph for each process and start a separate session (defining the
        # session explicitly isn't required in tf 2.x thanks to eager execution)
        nnet = CNN.load_nnet()
        print("LOADED")
        opt_mcts = MCTS(nnet)
        norm_mcts = OldMCTS(nnet)

        opt_visit_counts = save_time_benchmark(opt_mcts.get_visit_counts)
        norm_visit_counts = save_time_benchmark(norm_mcts.get_visit_counts)

        print("loaded")
        for plies in range(num_sims):
            tau = plies < num_sims // 2
            # Can use self.board because each process creates its own instance of the Pipeline class
            # each with its own memory allocated for board object
            bb = list(board.piecelist_to_bitboard())

            # more exploitation in the beginning
            visit_counts = opt_visit_counts(board, bb, funcname="mcts_opt")
            norm_visit_counts(board, bb, funcname="mcts_norm")

            pi = opt_mcts.get_pi(visit_counts)
            pi = opt_mcts.apply_tau(visit_counts, tau=tau)

            move = opt_mcts.select_action(board, pi)

            board.make_move(move)
            opt_mcts.reset(board.zobrist_key)
            norm_mcts.reset()

            plies += 1
            print(f"{plies=}")

            moves = LegalMoveGenerator.load_moves(board)
            status = board.get_terminal_status(len(moves))

            if status != -1: 
                print("QUIIIT")
                return

def get_bms():
    futures = []
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        for _ in range(mp.cpu_count()):
            futures.append(executor.submit(play))
    res = [f.result() for f in as_completed(futures)]
    return res

def analyze(a):
    avg = np.sum(a) / len(a)
    upper = np.max(a)
    lower = np.min(a)
    return upper, avg, lower

def get_diag():
    # get_bms()
    with open("visualizations/data", "rb") as f:
        data = Unpickler(f).load()
        opt = np.array(data["mcts_opt"])
        norm = np.array(data["mcts_norm"])
    opt = 8 / opt
    multi = 8 / norm

    return opt, multi, norm

def preprocess(opt, multi, norm):
    min_len = min(len(opt), len(multi), len(norm))
    piv = min_len // 2
    opt_tau_1, opt_tau_0 = opt[:piv], opt[piv:min_len]
    multi_tau_1, multi_tau_0 = multi[:piv], multi[piv:min_len]
    norm_tau_1, norm_tau_0 = norm[:piv], norm[piv:min_len]
    opt_diag_tau_0, multi_diag_tau_0, norm_diag_tau_0 = analyze(opt_tau_0), analyze(multi_tau_0), analyze(norm_tau_0)
    opt_diag_tau_1, multi_diag_tau_1, norm_diag_tau_1 = analyze(opt_tau_1), analyze(multi_tau_1), analyze(norm_tau_1)

    opt_tau_1 = np.clip(opt_tau_1, 0, 10)
    multi_tau_1 = np.clip(multi_tau_1, 0, 10)
    multi_tau_0 = np.clip(multi_tau_0, 0, 10)
    opt_tau_0 = np.clip(opt_tau_0, 0, 10)

    return opt_tau_1, opt_tau_0, multi_tau_1, multi_tau_0, norm_tau_1, norm_tau_0, \
        [
            [opt_diag_tau_0, multi_diag_tau_0, norm_diag_tau_0],
            [opt_diag_tau_1, multi_diag_tau_1, norm_diag_tau_1]
            ]

def visualize():
    import matplotlib.pyplot as plt
    import seaborn as sns
    opt_tau_1, opt_tau_0, multi_tau_1, multi_tau_0, norm_tau_1, norm_tau_0, \
         diags = preprocess(*get_diag())

    fig = plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(2, 2, hspace=0.5, wspace=0.2)
    ax_1 = fig.add_subplot(grid[0, 0])
    ax_2 = fig.add_subplot(grid[1, 0])
    ax_3 = fig.add_subplot(grid[0, 1])
    ax_4 = fig.add_subplot(grid[1, 1])
    bar_ax = [ax_3, ax_4]
    
    sns.histplot(opt_tau_0, label="Opt Reset", color="dodgerblue", binwidth=.1, kde=True, ax=ax_1)
    sns.histplot(multi_tau_0, label="Multiprocess", color="deeppink", binwidth=.1, kde=True, ax=ax_1)
    sns.histplot(norm_tau_0, label="Original", color="g", binwidth=.1, kde=True, ax=ax_1)

    sns.histplot(opt_tau_1, label="Opt Reset", color="dodgerblue", binwidth=.1, kde=True, ax=ax_2)
    sns.histplot(multi_tau_1, label="Multiprocess", color="deeppink", binwidth=.1, kde=True, ax=ax_2)
    sns.histplot(norm_tau_1, label="Original", color="g", binwidth=.1, kde=True, ax=ax_2)

    plt.xlim(0, 80)
    for tau in range(2):
        for i in range(3):
            bar_ax[tau].barh(["Opt Reset", "Multi", "Original"] , [diags[tau][0][i], diags[tau][1][i], diags[tau][2][i]])
    plt.show()

if __name__ == "__main__":
    visualize()