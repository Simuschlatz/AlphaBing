"""
Copyright (C) 2022-2023 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
import os
from . import CNN, MCTS, PlayConfig
from core.engine import Board, LegalMoveGenerator

import numpy as np
from random import shuffle

from tqdm import tqdm
from pickle import Pickler, Unpickler
import multiprocessing as mp
from copy import deepcopy
import logging


logger = logging.getLogger(__name__)

class SelfPlay:
    def __init__(self, nnet: CNN, board: Board) -> None:
        self.nnet = nnet
        self.board = board
        self.mcts = MCTS(nnet)
        self.training_data = []

    def augment_data(self, example):
        """
        Scales training data without additional MCTS search by:
        1. flipping bitboards and pi
        2. mirroring bitboards and pi
        
        adds augmented examples to :param eps_data:"""

        augmented = [example]
        bitboard, pi, side = example

        # NOTE flipping the board only works if the model takes in an input plane. This is due to the
        # fact that pi can't be flipped like the bitboards as pi's value changes with the moving side
        # 
        # flipped = self.board.mirror_bitboard(bitboard, 0)

        # This would be a bad training example detrimental for the model's training as pi is inaccurate
        # augumented.append([flipped, pi, 1-side])

        # Mirroring the board
        mirrored_bb = self.board.mirror_bitboard(bitboard)
        mirrored_pi = self.mcts.mirror_pi(pi)
        augmented.append([mirrored_bb, mirrored_pi, side])

        return augmented
        
    def execute_episode(self, moves, training_examples=None, board: Board=None, mcts: MCTS=None):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data. when a terminal state is reached, each training example's
        value v is the outcome z of that game from the sample's side's perspective.
        
        :param training_examples, board, mcts: only for multiprocessing. If not specified, returns
        a list of training examples. If specified, they extend training_examples. Form: (s, pi, v) 
        where s is the state represented
        
        as set of bitboards, pi is the probability distribution returned by MCTS, for v see above.
        :param training_examples: used for multiprocessing, a ``mp.Manager().list`` object, 
        shared memory containing the training examples from episode's self-play iteration
        """
        board = board or self.board
        mcts = mcts or self.mcts
        training_data = []
        plies, tau = 0, 1
        while True:
            bb = list(board.piecelist_to_bitboard())

            # more exploitation in the beginning
            if plies > PlayConfig.tau_decay_threshold:
                tau = round(PlayConfig.tau_decay_rate ** (plies - PlayConfig.tau_decay_threshold), 2)
            # tau = plies < PlayConfig.tau_decay_threshold
            pi = mcts.get_probability_distribution(board, bitboards=bb, moves=moves, tau=tau)
            side = board.moving_side

            # add the augmented examples from current position
            augmented_move_data = self.augment_data([bb, pi, side])
            training_data.extend(augmented_move_data)

            move = MCTS.best_action_from_pi(board, pi)
            # move = MCTS.random_action_from_pi(board, pi)

            board.make_move(move, search_state=False)
            plies += 1
            logger.debug(f"plies of current episode: {plies}")
            moves = LegalMoveGenerator.load_moves(board)
            status = board.get_terminal_status(len(moves))
            if status == -1: continue
            logger.info("self-play episode ended")
            # negative outcome for every example where the side was current (mated) moving side
            if training_examples is None:
                return [[ex[0], ex[1], 1 - 2 * ex[2] == board.moving_side] for ex in training_data]

            training_examples.extend([[ex[0], ex[1], 1 - 2 * ex[2] == board.moving_side] for ex in training_data])
            return

    @staticmethod
    def batch(iterable, batch_size):
        for ndx in range(0, len(iterable), batch_size):
            yield iterable[ndx:min(len(iterable), ndx+batch_size)]

    def train(self, parallel=False):
        """
        Performs self-play for ``PlayConfig.training_iterations`` iterations of 
        ``PlayConfig.self_play_eps`` episodes  each. The maximum length of training data is the 
        examples from the last ``PlayConfig.max_training_data_length``  iterations. After each 
        iteration, the neural  network is retrained.

        :param parallel: If True, each episode is executed on a a separate process
        """
        fen = self.board.load_fen_from_board()
        moves = LegalMoveGenerator.load_moves(self.board)
        for i in range(1, PlayConfig.training_iterations + 1):
            logger.debug(f"starting self-play iteration no. {i}")
            iteration_training_data = []

            if parallel:
                iteration_data = mp.Manager().list() # Shared list
                jobs = [mp.Process(target=self.execute_episode(moves, iteration_data, deepcopy(self.board), deepcopy(self.mcts))) for _ in range(PlayConfig.self_play_eps)]
                for processes in tqdm(self.batch(jobs, PlayConfig.max_processes)):
                    print("------starting process-------")
                    for p in processes: p.start()
                    for p in processes: p.join()
            else:
                for _ in tqdm(range(PlayConfig.self_play_eps), desc="Episodes"):
                    print("Starting episode...")
                    self.mcts = MCTS(self.nnet)
                    self.board = Board(fen)
                    eps_training_data = self.execute_episode(moves)
                    iteration_training_data.extend(eps_training_data)
                

            self.training_data.append(iteration_training_data)
            if len(self.training_data) > PlayConfig.max_training_data_length:
                self.training_data.pop(0)

            # collapse 3D list to 2d list
            train_examples = [example for iteration_data in self.training_data for example in iteration_data]  
            
            shuffle(train_examples)

            self.save_training_data()
            print(np.asarray(train_examples, dtype=object).shape)
            self.nnet.train(train_examples)
            self.nnet.save_checkpoint()
            
    def save_training_data(self, folder="core/Engine/AI/AlphaZero/checkpoints", filename="examples"):
        if not os.path.exists(folder):
            logger.info("Making folder for training data...")
            os.mkdir(folder)
        filepath = os.path.join(folder, filename)
        logger.info("Saving training data...")
        with open(filepath, "wb+") as f:
            Pickler(f).dump(self.training_data)
        logger.info("Done!")

    def load_training_data(self, folder="core/Engine/AI/AlphaZero/checkpoints", filename="examples"):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            logger.warning(f"Training data file {filepath} does not exist yet. Try running one iteration of self-play first.")
            return
        with open(filepath, "rb") as f:
            logger.info("Training examples file found. Loading content...")
            self.training_data = Unpickler(f).load()
            logger.info("Done!")

            
### JUST FOR TESTING ###         

import sys
import os
root = os.environ.get("CHEAPCHESS")
sys.path.append(root)
print(sys.path)

if __name__ == "__main__":
    mp.freeze_support()
    