from . import CNN, MCTS
from core.Engine import Board, PrecomputingMoves
import numpy as np

class SelfPlay:
    def __init__(self, nnet: CNN, board: Board) -> None:
        self.nnet = nnet
        self.board = board
        self.mcts = MCTS(nnet)
        self.training_data = []
    
    def execute_episode(self):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data. when a terminal state is reached, each training example's
        value v is the outcome z of that game from the sample's side's perspective.

        :return: a list of training examples. Form: (s, pi, v) where s is the state represented
        as set of bitboards, pi is the probability distribution returned by MCTS, for v see above.
        """
        training_data = []
        while True:
            bb = self.board.piecelist_to_bitboard()
            pi = self.mcts.get_probability_distribution(self.board, bb)
            side = self.board.moving_side

            training_data.append((bb, pi, side))

            move = MCTS.best_action_from_pi(pi)

            self.board.make_move(move, search_state=False)

            status = self.board.get_terminal_status()
            if status == -1: continue
            # negative outcome for every example where the side was current (mated) moving side
            return[(ex[0], ex[1], status * (1 - 2 * ex[2] == self.board.moving_side)) for ex in training_data]

    def train(self):
        pass

    