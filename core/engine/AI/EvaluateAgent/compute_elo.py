
from concurrent.futures import ProcessPoolExecutor, wait
from random import randint, choice
from core.engine import Board, LegalMoveGenerator
from core.engine.AI.AlphaZero import CNN, MCTS, EvaluationConfig
import os
from pickle import Pickler, Unpickler

from logging import getLogger
logger = getLogger(__name__)

# 0 ~ 999: K = 30; 1000 ~ 1999: K = 15; 2000 ~ 2999: K = 10; 3000 ~ : K = 5
K_TABLE = [30, 15, 10, 5]   

R_PRI = 40

def compute_elo(r0, r1, z):
    '''
    Compute the elo rating with method from https://www.xqbase.com/protocol/elostat.htm
    :param r0: player's elo rating
    :param r1: opponent elo rating
    :param z: game result: 1 = player wins, 0.5 = draw, 0 = opponent wins

    :return: The player's updated elo rating
    '''
    relative_elo = r1 - r0 - R_PRI
    we = 1 / (1 + 10 ** (relative_elo / 400))
    k0 = K_TABLE[min(r0, 3000) // 1000] # Limit highest coefficient K to 5
    # k1 = K_TABLE[min(r1, 3000) // 1000]
    rn0 = int(r0 + k0 * (z - we))
    # rn1 = int(r1 + k1 * (we - z))
    rn0 = max(rn0, 0) # Can't get rating below 0
    # rn1 = max(rn1, 0)
    return rn0


class Evaluator:
    def __init__(self, board):
        self.board = board

    def nnet_vs_random(self, network_score, random_score=200, board: Board=None):
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
                if is_randoms_turn: # Neural network won or draw
                    network_score = compute_elo(network_score, random_score, z)
                else: # Random agent won or draw
                    adjusted_z = 1 - z # Outcome from network's perspective
                    network_score = compute_elo(network_score, random_score, adjusted_z)
                print(f"neural network score: {network_score}")
                return network_score

            if is_randoms_turn:
                move = choice(moves)
            else:
                bitboards = list(board.piecelist_to_bitboard())
                pi = mcts.get_pi(board, bitboards, moves=moves)
                move = mcts.best_action_from_pi(board, pi)
                mcts.reset()

            print(f"{plies=}, {move=}")
            board.make_move(move)
            plies += 1

    def nnet_vs_nnet(self, old_rating, board: Board=None):
        board = board or self.board
        new_nnet = CNN.load_model()
        previous_nnet = CNN.load_model(new_model=False)

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
                # Update ratings
                if is_prev_nets_turn: # Neural network won or draw
                    # NOTE: The new network is assumed to play at least at the same level as
                    # the old network to avoid having to run hundreds of evaluation games until
                    # the new network's elo rating surpasses the old one's.
                    new_nnet_score = compute_elo(old_rating, old_rating, z)
                else: # Random agent won or draw
                    adjusted_z = 1 - z # Outcome from network's perspective
                    new_nnet_score = compute_elo(old_rating, old_rating, adjusted_z)
                print(f"new network score: {new_nnet_score}")
                return new_nnet_score

            
            bitboards = list(board.piecelist_to_bitboard())
            mcts = both_mcts[is_prev_nets_turn]
            pi = mcts.get_pi(board, bitboards, moves=moves)
            move = mcts.best_action_from_pi(board, pi)
            mcts.reset()

            print(f"{plies=}, {move=}")
            board.make_move(move)
            plies += 1


    def evaluate_worker(self, is_first_iteration: bool,):
        with ProcessPoolExecutor(max_workers=EvaluationConfig.max_processes) as executor:
            futures = []
            # I'd have loved to generalize a pit function that accepts any type of workers, 
            # random or nnet, and pits them against each other. However, since tf.Graph objects
            # aren't thread-safe, they have to be loaded them manually in the function called by 
            # the subprocesses. and can't be passed as a parameter or as part of an agent parameter.
            # Hence two separate pit functions.
            if is_first_iteration:
                for eps in range(EvaluationConfig.episodes):
                    futures.append(executor.submit(self.nnet_vs_random, 0))
            else:
                for eps in range(EvaluationConfig.episodes):
                    futures.append(executor.submit(self.nnet_vs_nnet, 0))

            
# def evaluate_worker(self, fen, nnet: CNN):
#     for i in range(10):
#         print(f"starting evaluation iteration n. {i}")
#         board = Board(fen)
#         mcts = MCTS(nnet)
#         nnet_ranking = pit_against_random(board, mcts, nnet_ranking)


