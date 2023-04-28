
import os
from manager import config
from . import CNN, MCTS, PlayConfig, TrainingConfig
from core.engine import Board, LegalMoveGenerator
from core.utils import time_benchmark
from random import shuffle

from tqdm import tqdm
from pickle import Pickler, Unpickler

from concurrent.futures import ProcessPoolExecutor, as_completed

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Pipeline:
    """
    The entire self-play / training / evaluation pipeline
    """
    def __init__(self, board: Board) -> None:
        from core.engine.ai.evaluate import Evaluator
        self.board = board
        self.evaluator = Evaluator(self.board)

    def augment_data(self, example: list):
        """
        Scales training data without additional MCTS search by:
        1. flipping bitboards and pi
        2. mirroring bitboards and pi
        
        :return: augmented training data
        """

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
        
    def execute_episode(self, moves: list[tuple], component_logger:logging.Logger=None):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data. Form: (s, π) where s is the state represented as set of bitboards, 
        π is the probability  distribution returned by MCTS. When a terminal state is reached, each 
        training example is extended by the outcome z of that game from the sample's side's perspective.

        Final Form of each example: (s, π, z)
        
        This function can be run in parallel (on multiple processes). In each process, it loads the
        tensorflow graph and starts a separate session.
        """

        logger = component_logger or logger
        logger.info("Starting episode")

        # Initialize the current tf graph for each process and start a separate session (defining the
        # session explicitly isn't required in tf 2.x thanks to eager execution)
        nnet = CNN.load_nnet()
        mcts = MCTS(nnet)

        training_data = []
        plies, tau = 0, 1
        while True:
            # Can use self.board because each process creates its own instance of the Pipeline class
            # each with its own memory allocated for board object
            bb = list(self.board.piecelist_to_bitboard())

            # more exploitation in the beginning
            visit_counts = mcts.get_visit_counts(self.board, bitboards=bb, moves=moves)
            pi = mcts.get_pi(visit_counts)
            # logger.debug(mcts.Nsa)
            # logger.debug("-" * 20)
            side = self.board.moving_side

            # add the augmented examples from current position
            augmented_move_data = self.augment_data([bb, pi, side])
            training_data.extend(augmented_move_data) # check if data is unique for each process
            
            # if plies > PlayConfig.tau_decay_threshold:
            #     tau = round(PlayConfig.tau_decay_rate ** (plies - PlayConfig.tau_decay_threshold), 2)
            tau = plies < PlayConfig.tau_decay_threshold
            # Apply temperature
            pi = mcts.apply_tau(visit_counts, tau=tau)

            move = MCTS.select_action(self.board, pi)

            self.board.make_move(move)
            plies += 1

            logger.info(f"{plies=} | {move=}")

            mcts.opt_reset(self.board.zobrist_key)
            logger.info(f"{mcts.subtree=}, {mcts.saved_sims=}")

            moves = LegalMoveGenerator.load_moves(self.board)
            status = self.board.get_terminal_status(len(moves))
            if status == -1: continue
            logger.info("self-play episode ended")
            # negative outcome for every example where the side was current (mated) moving side
            return [[ex[0], ex[1], 1 - 2 * ex[2] == self.board.moving_side] for ex in training_data]

    @staticmethod
    def batch(iterable, batch_size: int):
        for ndx in range(0, len(iterable), batch_size):
            yield iterable[ndx:min(len(iterable), ndx+batch_size)]
    @staticmethod
    def training_episode(training_examples, component_logger: logging.Logger=None):
        # print(training_examples)
        logger = component_logger or logger
        logger.info("Training episode started!")
        nnet = CNN.load_nnet()
        nnet.train(training_examples)
        return nnet

    @staticmethod
    def is_first_iteration(folder=TrainingConfig.checkpoint_location, filename=PlayConfig.examples_filename):
        """
        Determines whether the current iteration can train a new network"""
        return not os.path.exists(os.path.join(folder, filename))

    def start_pipeline(self):
        """
        Performs self-play for ``PlayConfig.training_iterations`` iterations of 
        ``PlayConfig.self_play_eps`` episodes  each. The maximum length of training data is the 
        examples from the last ``PlayConfig.max_training_data_length``  iterations. After each 
        iteration, the neural  network is retrained.

        In the first iteration, only self-play workers are executed. There can't be any training because there
        is no training data.
        In the next iterations, the new network is trained while all other processes generate new training data
        for the next iteration of training. 

        NOTE: This function should only be called from the main process
        """
        moves = LegalMoveGenerator.load_moves(self.board)
        
        for i in range(PlayConfig.training_iterations):
            logger.info(f"starting self-play iteration no. {i + 1}")
            iteration_training_data = []
            is_first_iteration = self.is_first_iteration()

            print(f"{PlayConfig.max_processes=} \n {is_first_iteration=}")

            with ProcessPoolExecutor(max_workers=PlayConfig.max_processes) as executor:
                futures = []
                # if not is_first_iteration:
                #     # Run the training worker on a separate process and not at the end of each iteration.
                #     # As training the network is a single-process job, it would leave all other 
                #     # processes unused. I decided not to run it parallel with the evaluatio workers,
                #     # although it would be more cronologically correct, because evaluation is optional
                #     # for the training pipeline and training itself is not.
                #     component_logger = logger.getChild(f"subprocess_training")
                #     prev_training_data = self.load_training_data()
                #     future = executor.submit(self.training_episode, prev_training_data, component_logger=component_logger)
                    
                for eps in range(PlayConfig.self_play_eps):
                    component_logger = logger.getChild(f"subprocess_{eps % PlayConfig.max_processes}")
                    futures.append(executor.submit(self.execute_episode, moves, component_logger=component_logger))

                results = [future.result() for future in as_completed(futures)]
                
                
            for res in results:
                iteration_training_data.extend(res)

            shuffle(iteration_training_data)
            self.save_training_data(iteration_training_data)
            logger.info(f"{len(iteration_training_data)=}")
            
            # Update the versions at the end, so that self-play agents of current iteration don't load new model
            if not is_first_iteration:
                nnet = future.result()
                CNN.update_checkpoint_versions(nnet)
            
            if config.evaluate:
                self.evaluator.evaluate_worker(is_first_iteration)
            
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

    @staticmethod
    def load_training_data(folder=TrainingConfig.checkpoint_location, filename=PlayConfig.examples_filename):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            logger.warning(f"Training data file {filepath} does not exist yet. Try running one iteration of self-play first.")
            return []
        logger.info("Training examples file found. Loading content...")
        with open(filepath, "rb") as f:
            training_data = Unpickler(f).load()
            logger.info("Done!")
            return training_data

            

    