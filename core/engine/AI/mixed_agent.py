from .agent_interface import Agent
from .ABMM.agent import AlphaBetaAgent
from .AlphaZero.agent import AlphaZeroAgent
from .ABMM.piece_square_tables import PieceSquareTable
from core.engine import Board, LegalMoveGenerator, PrecomputingMoves

class AlphaBetaZeroAgent(Agent):
    """
    A combination of AlphaBeta and AlphaZero
    """
    def __init__(self, above_max=-100):
        """
        The Alpha-Beta-Zero Agent.
        :param above_max: value added to the maximum value of the pst, 
        controlling weight of AlphaZero evaluation
        """
        self.aba = AlphaBetaAgent()
        self.aza = AlphaZeroAgent()
        self.m = PieceSquareTable.max_value + above_max

    def choose_action(self, board: Board):
        moves = LegalMoveGenerator.load_moves(board)

        aba_eval_table = self.aba.get_eval_table(board, moves)
        aba_action = self.aba.choose_action(board, aba_eval_table)

        aza_probs = self.aza.get_mcts_pi(board)
        aza_action = self.aza.choose_action(board, aza_probs)
        if aza_action == aba_action:
            return aba_action
        
        aba_action_space_index = PrecomputingMoves.move_index_hash[aba_action if board.opponent_side else board.flip_move(aba_action)]
        aba_value = aza_probs[aba_action_space_index] * self.m + aba_eval_table[aba_action]
        
        aza_action_space_index = PrecomputingMoves.move_index_hash[aza_action if board.opponent_side else board.flip_move(aza_action)]
        aza_value = aza_probs[aza_action_space_index] * self.m + aba_eval_table[aza_action]
        
        print(f"AlphaBeta Action: {aba_action}")
        print(f"AlphaBeta value: {aba_value}")
        print(f"AlphaZero Action: {aza_action}")        
        print(f"AlphaZero value: {aza_value}")

        return aza_action if aza_value > aba_value else aba_action
