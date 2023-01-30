from core.engine.AI.agent_interface import Agent
from core.engine import Board
from .search import Dfs

class AlphaBetaAgent(Agent):
    @staticmethod
    def get_eval_table(board: Board, moves):
        return Dfs.multiprocess_search(board, get_evals=True, moves=moves)

    @staticmethod
    def choose_action(eval_table: dict=None):
        """
        NOTE: This agent uses multiprocess search. To run single-process search,
        don't use the AlphaBetaAgent class, but Dfs.search instead.
        This class mainly serves as part of the AlphaBetaZeroAgent.
        """
        eval_table = eval_table or Dfs.multiprocess_search(eval_table)
        best_move = sorted(eval_table, key=lambda move: eval_table[move]).pop()
        return best_move