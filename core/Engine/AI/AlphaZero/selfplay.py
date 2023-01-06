from . import CNN, MCTS, PlayConfig
from core.Engine import Board, LegalMoveGenerator
import numpy as np
from random import shuffle

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
        plies, tau = 0, 1
        moves = LegalMoveGenerator.load_moves(self.board)
        while True:
            bb = list(self.board.piecelist_to_bitboard(adjust_perspective=True))

            if plies > PlayConfig.tau_decay_threshold:
                tau = PlayConfig.tau_decay_rate ** (plies - PlayConfig.tau_decay_threshold)

            pi = self.mcts.get_probability_distribution(self.board, bitboards=bb, moves=moves, tau=tau)
            side = self.board.moving_side

            bb = self.nnet.bitboard_to_input(bb)

            training_data.append((bb, pi, side))
            move = MCTS.best_action_from_pi(self.board, pi)

            self.board.make_move(move, search_state=False)
            plies += 1
            moves = LegalMoveGenerator.load_moves(self.board)
            status = self.board.get_terminal_status(len(moves))
            if status == -1: continue
            # negative outcome for every example where the side was current (mated) moving side
            return[(ex[0], ex[1], status * (1 - 2 * ex[2] == self.board.moving_side)) for ex in training_data]

    def train(self):
        """
        performs Play for
        """
        for i in range(1, PlayConfig.selfplay_iterations + 1):
            print(f"starting self-play iteration no. {i}")
            iteration_training_data = []

            for _ in range(PlayConfig.episodes):
                self.mcts = MCTS(self.nnet)
                eps_training_data = self.execute_episode()
                iteration_training_data.append(eps_training_data)

            self.training_data.append(iteration_training_data)
            if len(self.training_data) > PlayConfig.max_training_data_length:
                self.training_data.pop(0)

            # if not i % PlayConfig.steps_per_save:
            #     self.save_training_data()
            # collapse 3D list to 2d list
            train_examples = [example for iteration_data in self.training_data for example in iteration_data]           
            shuffle(train_examples)

            # self.nnet.train(train_examples)

            
    def load_training_data(self, folder, filename):
        pass

    def save_training_data(self, folder, filename):
        pass
            
            


    