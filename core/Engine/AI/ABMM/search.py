"""
Copyright (C) 2022-2023 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from core.engine.move_generator import LegalMoveGenerator
from core.engine.board import Board
from core.engine.AI.ABMM.eval_utility import Evaluation
from core.engine.AI.ABMM import order_moves, order_moves_pst
from core.utils.timer import time_benchmark
import multiprocessing as mp

class Dfs:
    checkmate_value = 9998
    draw = 0
    positive_infinity = 9999
    negative_infinity = -positive_infinity
    search_depth = 4

    # Ananlytics
    cutoffs = 0
    evaluated_nodes = 0

    @staticmethod
    def batch(iterable, batch_size):
        for ndx in range(0, len(iterable), batch_size):
            yield iterable[ndx:min(len(iterable), ndx+batch_size)]

    @classmethod
    @time_benchmark
    def multiprocess_search(cls, board, batch: bool=False, get_evals=False, moves=None) -> tuple:
        """
        Runs a search for board position leveraging multiple processors.
        :return: best move from current position
        :param batch: determines if all cpu cores are leveraged
        :param get_evals: if True, search returns a hash map of moves ordered by their value
        """
        # shared dict
        move_evals = mp.Manager().dict()
        moves = moves or LegalMoveGenerator.load_moves()
        if batch:
            jobs = [mp.Process(target=cls.search_for_move, args=(move, move_evals, cls.search_depth, board)) for move in moves]
            max_processes = mp.cpu_count()
            for processes in cls.batch(jobs, max_processes):
                for p in processes: p.start()
                for p in processes: p.join()
        else:
            jobs = []
            for move in moves:
                p = mp.Process(target=cls.search_for_move, args=(move, move_evals, cls.search_depth, board))
                jobs.append(p)
                p.start()
            for process in jobs: process.join()
        # print(sorted(move_evals, key=lambda move: move_evals[move]))

        if get_evals: return move_evals
        best_move = sorted(move_evals, key=lambda move: move_evals[move]).pop()
        return best_move

    @classmethod
    def search_for_move(cls, move, move_evals, depth, board: Board):
        """
        :return: best eval from current position for current player
        :param move_evals: dict shared between child processes
        """
        board.make_move(move, search_state=True)
        evaluation = -cls.alpha_beta_opt(board, depth-1, 1, cls.negative_infinity, cls.positive_infinity, 250)
        board.reverse_move(search_state=True)
        move_evals[move] = evaluation

    @classmethod
    def search(cls, board: Board, m=250, algorithm: str="optalphabeta"):
        """
        Starts traversal of board's possible configurations
        :param algorithm: "minimax", "alphabeta", optalphabeta"
        :param m: coefficient used in move ordering
        :return: best move possible
        """
        cls.evaluated_nodes = 0
        cls.cutoffs = 0
        best_move = None
        alpha = cls.positive_infinity
        beta = cls.negative_infinity
        best_eval = beta
        current_pos_moves = order_moves(LegalMoveGenerator.load_moves(board), board, m=m)
        cls.mate_found = False
        for move in current_pos_moves:
            board.make_move(move, search_state=True)
            match algorithm:
                case "optalphabeta":
                    evaluation = -cls.alpha_beta_opt(board, cls.search_depth - 1, 0, beta, alpha, m)
                case "alphabeta":
                    evaluation = cls.alpha_beta(board, cls.search_depth - 1, beta, alpha)
                case "minimax":
                    evaluation = cls.minimax(board, cls.search_depth - 1)
            board.reverse_move(search_state=True)
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = move
            if cls.mate_found:
                return best_move
        return best_move


    @classmethod
    def alpha_beta_opt(cls, board: Board, depth: int, plies: int, alpha: int, beta: int, m):
        """
        Optimized alpha-beta search with move ordering
        TODO: Transposition tables
        """
        if not depth:
            # return cls.quiescene(alpha, beta)
            cls.evaluated_nodes += 1
            return Evaluation.pst_shef(board)

        # if plies > 0:
        #     if board.is_repetition():
        #         return 0
            # alpha = max(alpha, -cls.checkmate_value + plies)
            # beta = min(beta, cls.checkmate_value - plies)
            # if alpha >= beta:
            #     return alpha

        moves = order_moves(LegalMoveGenerator.load_moves(board), board, m=m)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        num_moves = len(moves)
        status = board.get_terminal_status(num_moves)
        if status != -1:
            if status:
                # Return checkmated value instead of negative infinity so the ai still chooses a move even if it only detects
                # checkmates, as the checkmate value still is better than the initial beta of -infinity
                return -cls.checkmate_value
            # if terminal state but not mate, must be draw
            return cls.draw

        for move in moves:
            # traversing down the tree
            board.make_move(move, search_state=True)
            evaluation = -cls.alpha_beta_opt(board, depth - 1, plies + 1, -beta, -alpha, m)
            board.reverse_move(search_state=True)

            # Move is even better than best eval before,
            # opponent won't choose this move anyway so PRUNE YESSIR
            if evaluation >= beta:
                cls.cutoffs += 1
                return beta # Return -alpha of opponent, which will be turned to alpha in depth - 1
            # Keep track of best move for moving color
            alpha = max(evaluation, alpha)

        return alpha
        
    @classmethod
    def quiescene(cls, board: Board, alpha, beta):
        """
        A dfs-like algorithm used for chess searches, only considering captureing moves, thus helping the conventional
        search with misjudgment of situations when significant captures could take place in a depth below the search depth.
        :return: the best evaluation of a particular game state, only considering captures
        """ 
        # Evaluate current position before doing any moves, so a potentially good state for non-capture moves
        # isn't ruined by bad captures
        # cls.evaluated_positions += 1
        eval = Evaluation.pst_shef(board)
        cls.evaluated_nodes += 1
        # Typical alpha beta operations
        if eval >= beta:
            return beta
        alpha = max(eval, alpha)

        moves = order_moves_pst(LegalMoveGenerator.load_moves(generate_quiets=False), board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if board.is_terminal_state():
            status = board.get_status()
            if status:
                return -cls.checkmate_value
            if status == 0: 
                return cls.draw

        for move in moves:
            board.make_move(move, search_state=True)
            evaluation = -cls.quiescene(-beta, -alpha)
            board.reverse_move(search_state=True)
            # Move is even better than best eval before,
            # opponent won't choose move anyway so PRUNE YESSIR
            if evaluation >= beta:
                return beta
            # Keep track of best move for moving color
            alpha = max(evaluation, alpha)
        # If there are no captures to be done anymore, return the best evaluation
        return alpha


    @classmethod
    def minimax(cls, board: Board, depth):
        """
        A brute force dfs-like algorithm traversing every node of the game's 
        possible-outcome-tree of given depth
        with branching factor b and depth d time-complexity is O(b^d)
        :return: best move possible
        """
        # leaf node, return the static evaluation of current board
        if not depth:
            cls.evaluated_nodes += 1
            return Evaluation.pst_shef(board)
        
        moves = LegalMoveGenerator.load_moves()
        
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return -cls.checkmate_value

        best_evaluation = float("-inf")
        for move in moves:
            board.make_move(move, search_state=True)
            evaluation = -cls.minimax(board, depth - 1)
            best_evaluation = max(evaluation, best_evaluation)
            board.reverse_move(search_state=True)

        return best_evaluation
    
    @classmethod
    def alpha_beta(cls, board: Board, depth, alpha, beta):
        """
        Minimax with alpha-beta pruning
        """
        if not depth:
            cls.evaluated_nodes += 1
            return Evaluation.pst_shef(board)

        moves = LegalMoveGenerator.load_moves()
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        for move in moves:
            board.make_move(move, search_state=True)
            evaluation = -cls.alpha_beta(board, depth - 1, -beta, -alpha)
            board.reverse_move(search_state=True)
            # Move is even better than best eval before,
            # opponent won't choose move anyway so PRUNE YESSIR
            if evaluation >= beta:
                cls.cutoffs += 1
                return beta
            alpha = max(evaluation, alpha)
        return alpha

    @classmethod
    def get_best_eval(cls, board: Board, depth):
        alpha = cls.positive_infinity
        beta = cls.negative_infinity
        best_eval = beta
        current_pos_moves = order_moves(LegalMoveGenerator.load_moves(), board)
        cls.abort_search = False
        for move in current_pos_moves:
            if cls.abort_search:
                return best_eval
            board.make_move(move, search_state=True)
            evaluation = -cls.alpha_beta_opt(board, depth - 1, 0, beta, alpha)
            board.reverse_move(search_state=True)
            best_eval = max(evaluation, best_eval)
        return best_eval
            