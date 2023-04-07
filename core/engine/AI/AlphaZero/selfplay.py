
import os
from . import CNN, MCTS, PlayConfig, TrainingConfig
from core.engine import Board, LegalMoveGenerator
from core.utils import time_benchmark
import numpy as np
from random import shuffle

from tqdm import tqdm
from pickle import Pickler, Unpickler

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SelfPlayPipeline:
    def __init__(self, board: Board) -> None:
        self.board = board

    def augment_data(self, example: list):
        """
        Scales training data without additional MCTS search by:
        1. flipping bitboards and pi
        2. mirroring bitboards and pi
        
        adds augmented examples to :param eps_data:"""

        augmented = [example]
        bitboards, pi, side = example

        # NOTE flipping the board only works if the model takes in an input plane. This is due to the
        # fact that pi can't be flipped like the bitboards as pi's value changes with the moving side
        # 
        # flipped = self.board.mirror_bitboard(bitboard, 0)

        # This would be a bad training example detrimental for the model's training as pi is inaccurate
        # augumented.append([flipped, pi, 1-side])

        # Mirroring the board
        mirrored_bbs = self.board.mirror_bitboard(bitboards)
        mirrored_pi = MCTS.mirror_pi(pi)
        augmented.append([mirrored_bbs, mirrored_pi, side])

        return augmented
        
    def execute_episode(self, moves: list[tuple], training_examples=None, board: Board=None, component_logger:logging.Logger=None):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data with MCTS. when a terminal state is reached, each training 
        example's value v is the outcome z of that game from the sample's side's perspective.
        
        This function can be run in parallel (on multiple processes). In each process, it loads the
        tensorflow graph and starts a separate session.

        :param training_examples: only for multiprocessing. If not specified, this function returns
        a list of training examples. If specified, they're extended by training_examples. 
        Form: (s, pi, z) where s is the state represented as set of bitboards, pi is the probability 
        distribution returned by MCTS, for z see above.

        :param training_examples: used for multiprocessing, a ``mp.Manager().list`` object, 
        shared memory containing the training examples from episode's self-play iteration
        """

        logger = component_logger or logger
        board = board or self.board

        # Initialize the current tf graph for each process and start a separate session (defining the
        # session explicitly isn't required in tf 2.x thanks to eager execution)
        nnet = CNN.load_current_model()
        mcts = MCTS(nnet)

        training_data = []
        plies, tau = 0, 0
        # while True:
        mcts.reset()
        bb = list(board.piecelist_to_bitboard())

        # more exploitation in the beginning
        # if plies > PlayConfig.tau_decay_threshold:
        #     tau = round(PlayConfig.tau_decay_rate ** (plies - PlayConfig.tau_decay_threshold), 2)
        # tau = plies < PlayConfig.tau_decay_threshold
        pi = mcts.get_pi(board, bitboards=bb, moves=moves)
        # logger.debug(mcts.Nsa)
        # logger.debug("-" * 20)
        side = board.moving_side

        # add the augmented examples from current position
        augmented_move_data = self.augment_data([bb, pi, side])
        training_data.extend(augmented_move_data)

        move = MCTS.best_action_from_pi(board, pi)
        # move = MCTS.random_action_from_pi(board, pi)

        board.make_move(move)
        plies += 1

        logger.info(f"plies of current episode: {plies}")

        moves = LegalMoveGenerator.load_moves(board)
        status = board.get_terminal_status(len(moves))
        # if status == -1: continue
        logger.info("self-play episode ended")
        # negative outcome for every example where the side was current (mated) moving side
        if training_examples is None:
            return [[ex[0], ex[1], 1 - 2 * ex[2] == board.moving_side] for ex in training_data]

        training_examples.extend([[ex[0], ex[1], 1 - 2 * ex[2] == board.moving_side] for ex in training_data])
        return

    @staticmethod
    def batch(iterable, batch_size: int):
        for ndx in range(0, len(iterable), batch_size):
            yield iterable[ndx:min(len(iterable), ndx+batch_size)]



    def training_episode(training_examples):
        model = CNN.load_current_model()
        model.train(training_examples)

    def hybrid_pipeline(folder=TrainingConfig.checkpoint_location, filename=PlayConfig.examples_filename):
        return os.path.exists(os.path.join(folder, filename))

    def start_pipeline(self, parallel=False):
        """
        Performs self-play for ``PlayConfig.training_iterations`` iterations of 
        ``PlayConfig.self_play_eps`` episodes  each. The maximum length of training data is the 
        examples from the last ``PlayConfig.max_training_data_length``  iterations. After each 
        iteration, the neural  network is retrained.

        :param parallel: If True, each episode is executed on a a separate process

        NOTE: This function should only be called from the main process
        """
        assert __name__ != '__main__', "This function should only be called from the main process"

        fen = self.board.load_fen_from_board()
        moves = LegalMoveGenerator.load_moves(self.board)
        
        for i in range(PlayConfig.training_iterations):
            logger.info(f"starting self-play iteration no. {i + 1}")
            iteration_training_data = []
            hybrid_pipeline = self.hybrid_pipeline()

            print(f"{PlayConfig.max_processes=}")

            if parallel:
                with ProcessPoolExecutor(PlayConfig.max_processes) as executor:
                    futures = []
                    if hybrid_pipeline:
                        prev_training_data = self.load_training_data()
                        model = executor.submit(self.training_episode, prev_training_data).result()
                        
                    for eps in range(PlayConfig.self_play_eps):
                        component_logger = logger.getChild(f"process_{eps % PlayConfig.max_processes}")
                        futures.append(executor.submit(self.execute_episode, moves, component_logger=component_logger))
                
                results = [future.result() for future in as_completed(futures)]
                for res in results:
                    iteration_training_data.extend(res)
            else:
                for _ in tqdm(range(PlayConfig.self_play_eps), desc="Episodes"):
                    print("Starting episode...")
                    self.board = Board(fen)
                    eps_training_data = self.execute_episode(moves)
                    iteration_training_data.extend(eps_training_data)

            # shuffle(iteration_training_data)
            self.save_training_data()
            logger.info(f"{iteration_training_data=}")
            
            # Update the versions at the end, so that self-play agents of current iteration don't load new model
            if hybrid_pipeline:
                CNN.update_checkpoint_versions(model)

    @staticmethod
    def save_training_data(training_data: list, folder=TrainingConfig.checkpoint_location, filename=PlayConfig.examples_filename):
        if not os.path.exists(folder):
            logger.info("Making folder for training data...")
            os.mkdir(folder)
        filepath = os.path.join(folder, filename)
        logger.info("Saving training data...")
        with open(filepath, "wb+") as f:
            Pickler(f).dump(training_data)
        logger.info("Done!")

    def load_training_data(self, folder=TrainingConfig.checkpoint_location, filename=PlayConfig.examples_filename):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            logger.warning(f"Training data file {filepath} does not exist yet. Try running one iteration of self-play first.")
            return []
        with open(filepath, "rb") as f:
            logger.info("Training examples file found. Loading content...")
            training_data = Unpickler(f).load()
            logger.info("Done!")
            return training_data

            

    