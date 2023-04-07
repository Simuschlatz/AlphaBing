from core.engine.AI.agent_interface import Agent
from core.engine import Board
from .search import Dfs
from logging import getLogger
logger = getLogger(__name__)

class AlphaBetaAgent(Agent):
    @staticmethod
    def get_eval_table(board: Board, moves=None):
        return Dfs.multiprocess_search(board, get_evals=True, moves=moves)
        # return Dfs.search(board, algorithm="minimax")

    @staticmethod
    def choose_action(board, eval_table: dict=None):
        """
        NOTE: This agent uses multiprocess search. To run single-process search,
        don't use the AlphaBetaAgent class, but Dfs.search instead.
        This class mainly serves as part of the AlphaBetaZeroAgent.
        """
        eval_table = eval_table or AlphaBetaAgent.get_eval_table(board)
        best_move = sorted(eval_table, key=lambda move: eval_table[move]).pop()
        logger.info(f"EVAL: {eval_table[best_move]}")
        return best_move