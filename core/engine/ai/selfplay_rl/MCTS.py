import math
import numpy as np
from core.engine import Board, LegalMoveGenerator, PrecomputingMoves
from core.engine.ai.selfplay_rl import PlayConfig, CNN
from core.utils import time_benchmark
from typing import Iterable
from logging import getLogger
logger = getLogger(__name__)

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

    def __init__(self, nnet: CNN, config=PlayConfig):
        self.nnet = nnet
        self.config = config

        # W Values aren't stored because they are only of temporary use in each interation
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores each state s where the terminal code has been evaluated
        self.Vs = {}  # stores legal moves for board s
        
        # Just for reset optimization
        self.subtree = {} # stores all reached sub-states from each state at depth 1
        self.saved_sims = 0

    def opt_reset(self, moved_to: int):
        """
        Resets the MCTS search tree
        """
        subtree_to_keep = self.subtree[moved_to]
        self.saved_sims = len(subtree_to_keep)

        self.Qsa = {(s, a): q for (s, a), q in self.Qsa.items() if s in subtree_to_keep}
        self.Nsa = {(s, a): n for (s, a), n in self.Nsa.items() if s in subtree_to_keep} 

        self.Ns = {s: self.Ns[s] for s in subtree_to_keep} 
        self.Ps = {s: self.Ps[s] for s in subtree_to_keep} 
        self.Es = {s: self.Es[s] for s in subtree_to_keep} 
        self.Vs = {s: self.Vs[s] for s in subtree_to_keep} 
    
        self.subtree = {moved_to: subtree_to_keep}

    def search(self, board: Board, is_root=False, subtree_root=False, bitboards: list=None, moves: list[tuple]=None):
        """
        This function performs one iteration of MCTS. It recursively calls itself until a leaf node 
        is found. The move chosen at each point maximizes the upper confidence bound (Q(s|a) + U(s|a))

        Once a leaf node is found, the neural network is called to return an initial policy P and a 
        value v for the state. In case the leaf node is a terminal state, the outcome is returned.
        The values are then backpropagated up the search path and the values of Ns, Nsa, Qsa of each node
        are updated.

        The board states are represented as a 64-bit zobrist-hashed number of that board. Actions are 
        determined by finding the move in the action space vector corresponding to the policy vector index

        :param is_root: True if current state is the root state
        :param bitboards: bitboards of current state as a list. If None, they're generated
        """

        # NOTE: the term 'action' is synonymous with 'move' in this method for congruence with the paper
        s = board.zobrist_key
        moves = moves or LegalMoveGenerator.load_moves(board)

        if not is_root:
            self.subtree[subtree_root] = self.subtree.get(subtree_root, []) + [s]

        # Check if position was already statically evaluated
        if s not in self.Es:
            status = board.get_terminal_status(len(moves))
            self.Es[s] = status

        if self.Es[s] != -1:
            return -self.Es[s]

        if board.moving_side: moves = board.flip_moves(moves)

        # Check if position was expanded
        if s not in self.Ps:
            # leaf node
            state_planes = bitboards or board.piecelist_to_bitboard()
            p, v = self.nnet.predict(state_planes)
            self.Ps[s] = p[0] # CNN output is two-dimensional

            valids = LegalMoveGenerator.bitvector_legal_moves(legal_moves=moves) # make this binary maybe?
            # masking invalid moves
            self.Ps[s] = self.Ps[s] * valids
            sum_Ps = np.sum(self.Ps[s])
            
            if sum_Ps:
                self.Ps[s] /= sum_Ps  # renormalize
            else:
                # if all valid moves were masked, make all valid moves equally probable
                logger.error("All valid moves were masked, doing a workaround. Please check your NN training process.")
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        num_moves = len(moves)
        if is_root:
            # dirichlet noise for exploration
            eps = self.config.noise_eps
            noise = np.random.dirichlet([self.config.dirichlet_alpha] * num_moves)
        else:
            eps = 0
            noise = np.zeros(num_moves) # [0] * num_moves (inconsistent with above)

        # No leaf node, traverse tree
        valids = self.Vs[s]
        best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for i, move in enumerate(moves):
            a = PrecomputingMoves.move_index_hash[move]
            if (s, a) in self.Qsa:
                q = self.Qsa[(s, a)]
                u = self.config.cpuct * ((1-eps) * self.Ps[s][a] + eps * noise[i]) * \
                    math.sqrt(self.Ns[s]) / (1 + self.Nsa[(s, a)])
            else:
                q = 0
                u = self.config.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + self.config.noise_eps)  # Q = 0

            if q + u > best:
                best = u
                best_act = a

        a = best_act
        move = PrecomputingMoves.action_space_vector[a]
        # Flipping the move back around. Much more efficient than using bigger architecture, 
        # more labels, masking those labels...
        if board.moving_side: move = board.flip_move(move)
        board.make_move(move, search_state=True)
        # If we're at root state, we specify the next state (depth 1), then it stays the same
        if is_root:
            subtree_root = board.zobrist_key
        v = self.search(board, subtree_root=subtree_root)

        board.reverse_move(search_state=True)

        # Update Qsa, Nsa and Ns
        if (s, a) in self.Qsa:
            self.Nsa[(s, a)] += 1
            self.Qsa[(s, a)] = ((self.Nsa[(s, a)] - 1) * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)])
        else:
            self.Nsa[(s, a)] = 1
            self.Qsa[(s, a)] = v

        self.Ns[s] += 1
        return -v

    @time_benchmark
    def get_visit_counts(self, board: Board, bitboards: list, moves=None):
        """
        Performs a number of MCTS simulations with root state of current ``board``.
        :return: The visit counts at depth 1 used to calculate π and to apply exploration
        temperature to π

        The reason why this method does not return π is because the visit counts are needed 
        to apply the temperature when selecting a move and to calculate π where each action 
        prob is directly proportional to its visit count (used to train the network). As the 
        network learns the improved probabilities of MCTS, it cannot be trained using π with 
        tau applied (inconsistent and inefficient for training), therefore both probabilities
        have to be calculated.
        """
        for i in range(self.config.simulations_per_move - self.saved_sims):
            # logger.info(f"starting simulation n. {i}")
            self.search(board, is_root=True, bitboards=bitboards, moves=moves)

        s = board.zobrist_key
        # storing the visit counts
        visit_counts = np.array([self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in PrecomputingMoves.action_space_range])
        return visit_counts

    @staticmethod
    def get_pi(visit_counts):
        """
        Normalizes the visit counts
        :return: π where π_a ∝ N(s|a): The probability distribution used for policy iteration
        """
        return visit_counts / np.sum(visit_counts)

    @staticmethod
    def apply_tau(visit_counts: np.ndarray, tau=1):
        """
        :param tau: Exploration temperature - high: exploration, low: exploitation
        :return: π where π_a ∝ N(s|a)^(1/tau): The probability distribution used for move selection
        """
        # Choose best move ...
        # ... deterministically for exploitation
        if not tau: 
            # Infinitesimal temperature -> asymptotically 0 -> one-hot encode
            best_a = np.random.choice(np.argmax(visit_counts).flatten())
            print(f"{best_a=}")
            probs = np.zeros(PrecomputingMoves.action_space)
            probs[best_a] = 1
            return probs
        # ... stochastically for exploration
        visit_counts = visit_counts ** (1. / tau)
        visis_counts_sum = float(np.sum(visit_counts))
        probs = visit_counts / visis_counts_sum # renormalize
        return probs

    @staticmethod
    def select_action(board: Board, pi: np.ndarray):
        """
        :return: A move chosen from the action space where each action is associated 
        with its corresponding value in the probability distribution pi
        NOTE: the perspective-dependent move is readjusted to the absolute squares
        """
        # If tau in the search was high, pi will allow for more stocasticity
        # If tau in the search was low, the selection of a move will be fully deterministic as pi is one-hot encoded
        # print(*pi[np.argwhere(pi)])
        a = np.random.choice(PrecomputingMoves.action_space_range, p=pi)
        move = PrecomputingMoves.action_space_vector[a]
        return board.flip_move(move) if board.moving_side else move

    @staticmethod
    def mirror_pi(pi):
        """
        Mirrors probability distribution
        """
        mirrored_pi = np.zeros(PrecomputingMoves.action_space)
        for a, v in enumerate(pi):
            # Skip illegal moves
            if not v: continue
            move = PrecomputingMoves.action_space_vector[a]
            mirrored_move = Board.mirror_move(move)
            # Get action space index of mirrored move
            mirrored_index = PrecomputingMoves.move_index_hash[mirrored_move]
            mirrored_pi[mirrored_index] = v
        return mirrored_pi
