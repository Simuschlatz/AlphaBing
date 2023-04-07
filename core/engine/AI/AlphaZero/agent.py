from . import MCTS, CNN
from core.engine import Board
from core.engine.AI.agent_interface import Agent

class AlphaZeroAgent(Agent):
    """
    Alpha Zero Agent for the engine to interact with
    handles playing and training
    """
    def __init__(self) -> None:
        nnet = CNN()
        self.mcts = MCTS(nnet)
    
    def get_mcts_pi(self, board: Board):
        bitboards = list(board.piecelist_to_bitboard())
        pi = self.mcts.get_pi(board, bitboards=bitboards)
        return pi

    def choose_action(self, board: Board, pi=[]):
        pi = list(pi) or self.get_mcts_pi(board)
        action = self.mcts.best_action_from_pi(board, pi)
        return action