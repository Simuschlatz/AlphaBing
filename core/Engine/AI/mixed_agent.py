from .agent_interface import Agent
from .ABMM.agent import AlphaBetaAgent
from .AlphaZero.agent import AlphaZeroAgent
from . import Dfs
from core.Engine import Board, LegalMoveGenerator

class AlphaBetaZeroAgent(Agent):
    """
    A combination of AlphaBeta and AlphaZero
    """
    def __init__(self, board: Board):
        self.aba = AlphaBetaAgent()
        self.aza = AlphaZeroAgent()
        self.board = board
    
    def choose_action(self):
        moves = LegalMoveGenerator.load_moves(self.board)
        aba_eval = self.aba.get_eval_table(self.board)
        aba_action = self.aba.choose_action()
    