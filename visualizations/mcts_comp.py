if __name__ == "__main__":
    import sys
    import os
    root = os.environ.get("CHEAPCHESS")
    sys.path.append(root)
    print(sys.path)


    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing as mp
    from pickle import Unpickler

from core.utils import save_time_benchmark, BoardUtility
from core.engine import Board, LegalMoveGenerator

from core.engine.ai.selfplay_rl import MCTS, CNN
from core.engine.ai.selfplay_rl.MCTS import OldMCTS
from logging import getLogger
logger = getLogger(__name__)

fen = BoardUtility.get_inital_fen(True, True)

def play(plies=15):
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
        plies = 0
        for _ in range(plies):
            # Can use self.board because each process creates its own instance of the Pipeline class
            # each with its own memory allocated for board object
            bb = list(board.piecelist_to_bitboard())

            # more exploitation in the beginning
            visit_counts = opt_visit_counts(board, bb, funcname="mcts_opt")
            norm_visit_counts(board, bb, funcname="mcts_norm")

            try:
                pi = opt_mcts.get_pi(visit_counts)
                pi = opt_mcts.apply_tau(visit_counts)

                move = opt_mcts.select_action(board, pi)

                print("GOT MOVE")
                board.make_move(move)
                opt_mcts.reset(board.zobrist_key)
                norm_mcts.reset()

                plies += 1
                print(f"{plies=}")

                moves = LegalMoveGenerator.load_moves(board)
                status = board.get_terminal_status(len(moves))
            except Exception as e:
                print(e)
            if status != -1: 
                print("QUIIIT")
                return

def get_bms():
    futures = []
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        for _ in range(mp.cpu_count()):
            futures.append(executor.submit(play))
    res = [f.result() for f in as_completed(futures)]

def visualize():
    # get_bms()
    with open("visualizations/data", "rb") as f:
        data = Unpickler(f).load()
        opt = data["mcts_opt"]
        norm = data["mcts_norm"]
    opt_avg = sum(opt) / len(opt)
    norm_avg = sum(norm) / len(norm)
    opt_max = max(opt)
    norm_max = max(norm)
    opt_min = min(opt)
    norm_min = min(norm)

    print(opt_avg, norm_avg, opt_min, norm_min)

if __name__ == "__main__":
    visualize()