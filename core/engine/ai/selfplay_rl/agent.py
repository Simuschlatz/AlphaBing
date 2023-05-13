from . import MCTS, CNN
from core.engine import Board
from core.engine.ai.agent_interface import Agent

class AlphaZeroAgent(Agent):
    """
    Alpha Zero Agent for the engine to interact with
    handles playing and training
    """
    def __init__(self) -> None:
        nnet = CNN()
        self.mcts = MCTS(nnet)
    
    def get_mcts_pi(self, board: Board):
        """
        Get the MCTS probability distribution for current state of ``board``
        """
        bitboards = list(board.piecelist_to_bitboard())
        pi = self.mcts.get_visit_counts(board, bitboards=bitboards)
        return pi

    def choose_action(self, board: Board, pi=[]):
        """
        Chooses the best action from pi.
        :param pi: MCTS probability distribution for current state of ``board``. If None, it's generated.
        """
        pi = list(pi) or self.mcts.apply_tau(self.get_mcts_pi(board), tau=0)
        action = self.mcts.select_action(board, pi)
        board.make_move(action)
        self.mcts.reset(board.zobrist_key)
        print(f"{self.mcts.subtree=}, {len(self.mcts.subtree[board.zobrist_key])=}")
        board.reverse_move()
        return action