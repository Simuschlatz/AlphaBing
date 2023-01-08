from . import MCTS, CNN
from core.Engine import Board
from core.Engine.AI.agent_interface import Agent

class AlphaZeroAgent(Agent):
    """
    Alpha Zero Agent for the Engine to interact with
    handles playing and training
    """
    def __init__(self) -> None:
        nnet = CNN()
        self.mcts = MCTS(nnet)
    
    def get_mcts_pi(self, board):
        bitboards = board.piecelist_to_bitboard(adjust_perspective=True)
        pi = self.mcts.get_probability_distribution(board, bitboards=bitboards)
        return pi

    def choose_action(self, board: Board, pi=None):
        pi = pi or self.mcts.get_probability_distribution(board, bitboards=list(board.piecelist_to_bitboard(True)))
        action = self.mcts.best_action_from_pi(board, pi)
        return action