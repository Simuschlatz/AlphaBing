
from concurrent.futures import ProcessPoolExecutor, wait
from random import randint, choice
from core.engine import Board, LegalMoveGenerator
from core.engine.AI.AlphaZero import CNN, MCTS, EvaluationConfig
import os
from pickle import Pickler, Unpickler

import logging
logger = logging.getLogger(__name__)

# 0 ~ 999: K = 30; 1000 ~ 1999: K = 15; 2000 ~ 2999: K = 10; 3000 ~ : K = 5
K_TABLE = [30, 15, 10, 5]   

R_PRI = 40

def compute_elo(player_elo: int, opponent_elo: int, z: float):
    '''
    Compute the elo rating with method from https://www.xqbase.com/protocol/elostat.htm
    :param z: game outcome: 1 = player wins, 0.5 = draw, 0 = opponent wins

    :return: The player's updated elo rating
    '''
    relative_elo = opponent_elo - player_elo - R_PRI
    we = 1 / (1 + 10 ** (relative_elo / 400))
    k0 = K_TABLE[min(player_elo, 3000) // 1000] # Limit highest coefficient K to 5
    # k1 = K_TABLE[min(r1, 3000) // 1000]
    rn0 = int(player_elo + k0 * (z - we))
    # rn1 = int(r1 + k1 * (we - z))
    rn0 = max(rn0, 0) # Can't get rating below 0
    # rn1 = max(rn1, 0)
    return rn0


class Evaluator:
    def __init__(self, board):
        self.board = board

    def nnet_vs_random(self, board: Board=None, component_logger: logging.Logger=None):
        logger = component_logger or logger
        board = board or self.board
        nnet = CNN()
        nnet.load_checkpoint()
        mcts = MCTS(nnet)

        randoms_turn = randint(0, 1)

        plies = 0
        while True:
            moves = LegalMoveGenerator.load_moves(board)
            game_over = board.is_terminal_state(len(moves))
            is_randoms_turn = plies % 2 == randoms_turn

            if game_over:
                status = board.get_terminal_status(len(moves)) # 0 or 1
                z = max(1, status + .5)
                # Update ratings
                return z if is_randoms_turn else 1-z

            if is_randoms_turn:
                move = choice(moves)
            else:
                bitboards = list(board.piecelist_to_bitboard())
                pi = mcts.get_pi(board, bitboards, moves=moves)
                move = mcts.best_action_from_pi(board, pi)
                mcts.reset()

            logger.info(f"{plies=}, {move=}")
            board.make_move(move)
            plies += 1

    def nnet_vs_nnet(self, board: Board=None, component_logger: logging.Logger=None):
        """
        """
        logger = component_logger or logger
        board = board or self.board
        new_nnet = CNN.load_nnet()
        previous_nnet = CNN.load_nnet(current_model=False)

        new_mcts = MCTS(new_nnet)
        previous_mcts = MCTS(previous_nnet)

        both_mcts = [new_mcts, previous_mcts]

        prev_nnets_turn = randint(0, 1)

        plies = 0
        while True:
            moves = LegalMoveGenerator.load_moves(board)
            game_over = board.is_terminal_state(len(moves))
            is_prev_nets_turn = plies % 2 == prev_nnets_turn

            if game_over:
                status = board.get_terminal_status(len(moves)) # 0 or 1
                z = max(1, status + .5)
                # Return 1 if new network won, 0 if old network won, .5 if draw
                return z if is_prev_nets_turn else z-1

            
            bitboards = list(board.piecelist_to_bitboard())
            mcts = both_mcts[is_prev_nets_turn]
            pi = mcts.get_pi(board, bitboards, moves=moves)
            move = mcts.best_action_from_pi(board, pi)
            mcts.reset()

            logger.info(f"{plies=}, {move=}")
            board.make_move(move)
            plies += 1

    @staticmethod
    def compute_win_rate(outcomes: list[int | float]):
        return outcomes.count(1) / len(outcomes)

    @staticmethod
    def update_elo(outcomes: list[int | float], rating_1: int, rating_2: int):
        """
        Updates ``rating_1``.
        :param outcomes: list of game outcomes from player_1's perspective
        """
        for z in outcomes:
            rating_1 = compute_elo(rating_1, rating_2, z)
        return rating_1

    @staticmethod
    def save_eval(value, filename: str, folder=EvaluationConfig.checkpoint_location):
        """
        Adds value to elo rating or win-rate history
        """

        hist = Evaluator.get_rating_history(filename, folder=folder)
        hist.append(value)

        if not os.path.exists(folder):
            logger.info("Making folder for elo or win-rate rating history...")
            os.mkdir(folder)

        filepath = os.path.join(folder, filename)
        logger.info("Saving rating...")
        with open(filepath, "wb+") as f:
            Pickler(f).dump(hist)
        logger.info("Done!")

    @staticmethod
    def get_eval_history(filename: str, folder=EvaluationConfig.checkpoint_location) -> list:
        """
        :return: list of elo ratings or win-rates recorded in previous iterations of evaluation. 
        If file does not exist, it returns an empty list
        """
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            logger.warning(f"Elo rating history file {filepath} does not exist yet.")
            return [0]
        logger.info("Elo rating or win-rate history file found. Loading content...")
        with open(filepath, "rb") as f:
            training_data = Unpickler(f).load()
            logger.info("Done!")
            return training_data

    def evaluate_worker(self, is_first_iteration: bool,):
        with ProcessPoolExecutor(max_workers=EvaluationConfig.max_processes) as executor:
            futures = []
            # I'd have loved to generalize a pit function that accepts any type of workers, 
            # random or nnet, and pits them against each other. However, since tf.Graph objects
            # aren't thread-safe, they have to be loaded them manually in the function called by 
            # the subprocesses. and can't be passed as a parameter or as part of an agent parameter.
            # Hence two separate pit functions.
            if is_first_iteration:
                # Get the rating of first network by using baseline agent
                for eps in range(EvaluationConfig.episodes):
                    component_logger = logger.getChild(f"subprocess_{eps % EvaluationConfig.max_processes}")
                    futures.append(executor.submit(self.nnet_vs_random, component_logger=component_logger))
                # Set old elo to random agent's baseline rating
                old_elo = EvaluationConfig.baseline_rating
                new_elo = 0
            else:
                for eps in range(EvaluationConfig.episodes):
                    component_logger = logger.getChild(f"subprocess_{eps % EvaluationConfig.max_processes}")
                    futures.append(executor.submit(self.nnet_vs_nnet, component_logger=component_logger))
                # NOTE: The new network is assumed to play at least at the same level as
                # the old network to avoid having to run hundreds of evaluation games until
                # the new network's elo rating surpasses the old one's.
                old_elo = self.get_eval_history(EvaluationConfig.elo_rating_filename).pop()
                new_elo = old_elo
        outcomes = [future.result() for future in futures]
        win_rate = self.compute_win_rate(outcomes)
        updated_elo = self.update_elo(outcomes, new_elo, old_elo)
        
        self.save_eval(win_rate, EvaluationConfig.win_rate_filename)
        self.save_eval(updated_elo, EvaluationConfig.elo_rating_filename)

# def evaluate_worker(self, fen, nnet: CNN):
#     for i in range(10):
#         print(f"starting evaluation iteration n. {i}")
#         board = Board(fen)
#         mcts = MCTS(nnet)
#         nnet_ranking = pit_against_random(board, mcts, nnet_ranking)


