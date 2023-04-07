
from concurrent.futures import ProcessPoolExecutor, wait
from multiprocessing import Value
# from datetime import datetime
from random import randint, choice
from core.engine import Board, LegalMoveGenerator
from core.engine.AI.AlphaZero import CNN, MCTS, EvaluationConfig
# from multiprocessing import Manager
# from threading import Thread
# from time import time, sleep
# from collections import defaultdict
# from multiprocessing import Lock
# from random import random, randint
# import numpy as np

from logging import getLogger
logger = getLogger(__name__)

# 0 ~ 999: K = 30; 1000 ~ 1999: K = 15; 2000 ~ 2999: K = 10; 3000 ~ : K = 5
K_TABLE = [30, 15, 10, 5]   

R_PRI = 40

def compute_elo(r0, r1, w):
    '''
    Compute the elo rating with method from https://www.xqbase.com/protocol/elostat.htm
    :param r0: player's elo rating
    :param r1: opponent elo rating
    :param w: game result: 1 = player wins, 0.5 = draw, 0 = opponent wins
    '''
    relative_elo = r1 - r0 - R_PRI
    we = 1 / (1 + 10 ** (relative_elo / 400))
    k0 = K_TABLE[min(r0, 3000) // 1000] # Limit highest coefficient K to 5
    k1 = K_TABLE[min(r1, 3000) // 1000]
    rn0 = int(r0 + k0 * (w - we))
    rn1 = int(r1 + k1 * (we - w))
    rn0 = max(rn0, 0) # Can't get rating below 0
    rn1 = max(rn1, 0)
    return rn0, rn1


def pit_against_random(board: Board, mcts: MCTS, worker_score, random_score=200):
    random_turn = randint(0, 1)
    plies = 0

    while True:
        moves = LegalMoveGenerator.load_moves(board)
        game_over = board.is_terminal_state(len(moves))

        is_random_turn = plies % 2 == random_turn
        if game_over:
            outcome = board.get_terminal_status(len(moves)) # 0 or 1
            w = max(1, outcome + .5)
            # Update ratings
            if is_random_turn:
                _, worker_score = compute_elo(random_score, worker_score, w)
                print("Random agent won!")
            else: 
                worker_score, _ = compute_elo(worker_score, random_score, w)
                print("Neural network won!")
            print(f"neural network score: {worker_score}")
            return worker_score


        if is_random_turn:
            move = choice(moves)
        else:
            bitboards = list(board.piecelist_to_bitboard())
            pi = mcts.get_probability_distribution(board, bitboards, moves=moves)
            move = mcts.best_action_from_pi(board, pi)

        print(f"{plies=}, {move=}")
        board.make_move(move)
        plies += 1

class Evaluator:
    def __init__(self, config: EvaluationConfig):
        self.config = config

    def evaluate_worker(self, fen, nnet: CNN):
        nnet_ranking = 0
        with ProcessPoolExecutor(max_workers=self.config.max_processes) as executor:
            futures = []
            for i in range(10):
                print(f"starting evaluation iteration n. {i}")
                board = Board(fen)
                mcts = MCTS(nnet)
                nnet_ranking = pit_against_random(board, mcts, nnet_ranking)

def evaluate_worker(self, fen, nnet: CNN):
    for i in range(10):
        print(f"starting evaluation iteration n. {i}")
        board = Board(fen)
        mcts = MCTS(nnet)
        nnet_ranking = pit_against_random(board, mcts, nnet_ranking)


