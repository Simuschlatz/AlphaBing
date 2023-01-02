import logging
import math
import numpy as np
from core.Engine import Board, LegalMoveGenerator

EPS = 1e-8

log = logging.getLogger(__name__)

'''
- statically evaluate node, if terminal node: return -value
- if leaf node:
    1. get p & v from NN
    2. mask illegal moves in p, normalize masked values
    3. update Ns and legal Moves
- else:
    1. select move with highest Qsa + Usa
    2. make move
    3. MCTS for next position
    4. get the value v of leaf node (when recursion base case is met)
    5. update Qsa and Nsa
        - if a was taken from s before:
            1. N ++
            2. Qsa = ((Nsa - 1) * Qsa + v) / Nsa)
        - else:
            1. Qsa = v
            2. Nsa = 1]
    
    return - v
'''


class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, nnet, config):
        self.nnet = nnet
        self.config = config
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

    def getActionProb(self, board: Board, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS on ```board```.
        :return: probs: a policy vector where the probability of the ith action is proportional to 
        Nsa[(s,a)]**(1./temp)
        """
        pass

    def search(self, board: Board):
        """
        This function performs one iteration of MCTS. It recursively calls itself until a leaf node 
        is found. The move chosen at each point maximizes the upper confidence bound (Q(s|a) + U(s|a))

        Once a leaf node is found, the neural network is called to return an initial policy P and a 
        value v for the state. In case the leaf node is a terminal state, the outcome is returned.
        The values are then backpropagated up the search path and the values of Ns, Nsa, Qsa of each node
        are updated.
        """
        pass

        