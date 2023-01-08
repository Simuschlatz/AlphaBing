from .agent_interface import Agent
from .ABMM.agent import AlphaBetaAgent
from .AlphaZero.agent import AlphaZeroAgent
from .ABMM.piece_square_tables import PieceSquareTable
from core.Engine import Board, LegalMoveGenerator, PrecomputingMoves

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

        aba_eval_table = self.aba.get_eval_table(self.board, moves)
        aba_action = self.aba.choose_action(aba_eval_table)

        print(f"AlphaBeta Action: {aba_action}")
        aza_probs = self.aza.get_mcts_pi(self.board)
        aza_action = self.aza.choose_action(self.board, aza_probs)
        print(f"AlphaZero Action: {aza_action}")        
        if aza_action == aba_action:
            return aba_action
        aba_action_space_index = PrecomputingMoves.move_index_hash[aba_action]
        aba_value = aza_probs[aba_action_space_index] * PieceSquareTable.max_value + aba_eval_table[aba_action]
        print(f"AlphaBeta value: {aba_value}")
        
        aza_action_space_index = PrecomputingMoves.move_index_hash[aza_action]
        aza_value = aza_probs[aza_action_space_index] * PieceSquareTable.max_value + aba_eval_table[aza_action]
        print(f"AlphaZero value: {aza_value}")

        return aza_action if aza_value > aba_value else aba_action


