"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
import copy
from core.Engine.move_generator import LegalMoveGenerator
from core.Engine.board import Board
from core.Engine.AI.ABMM.eval_utility import Evaluation
from core.Engine.AI import order_moves, order_moves_pst
import multiprocessing as mp

class Dfs:
    checkmate_value = 9998
    draw = 0
    positive_infinity = 9999
    negative_infinity = -positive_infinity
    search_depth = 4

    @staticmethod
    def batch(iterable, batch_size):
        for ndx in range(0, len(iterable), batch_size):
            yield iterable[ndx:min(len(iterable), ndx+batch_size)]

    @classmethod
    def multiprocess_search(cls, board, batch: bool=True) -> tuple:
        """
        Runs a search for board position leveraging multiple processors.
        :return: best move from current position
        :param batch: determines if all cpu cores are leveraged
        """
        best_move = None
        # shared dict
        move_evals = mp.Manager().dict()
        current_pos_moves = order_moves(LegalMoveGenerator.load_moves(), board)
        if batch:
            jobs = [mp.Process(target=cls.search_for_move, args=(move, move_evals, cls.search_depth, board)) for move in current_pos_moves]
            max_processes = mp.cpu_count() - 1
            for processes in cls.batch(jobs, max_processes):
                for p in processes: p.start()
                for p in processes: p.join()
        else:
            jobs = []
            for move in current_pos_moves:
                p = mp.Process(target=cls.search_for_move, args=(move, move_evals, cls.search_depth, board))
                jobs.append(p)
                p.start()
            for process in jobs: process.join()
        # print(sorted(move_evals, key=lambda move: move_evals[move]))

        best_move = sorted(move_evals, key=lambda move: move_evals[move]).pop()
        return best_move

    @classmethod
    def search_for_move(cls, move, move_evals, depth, board):
        """
        :return: best eval from current position for current player
        :param move_evals: dict shared between child processes
        """
        # make independent copy of board so attributes eg. board history don't get messed up
        board = copy.deepcopy(board)
        board.make_move(move)
        evaluation = -cls.alpha_beta_opt(board, depth-1, 1, cls.negative_infinity, cls.positive_infinity)
        board.reverse_move()
        move_evals[move] = evaluation

    @classmethod
    def search(cls, board: Board):
        """
        Starts traversal of board's possible configurations
        :return: best move possible
        """
        best_move = None
        alpha = cls.positive_infinity
        beta = cls.negative_infinity
        best_eval = beta
        current_pos_moves = order_moves(LegalMoveGenerator.load_moves(board), board)
        cls.mate_found = False
        for move in current_pos_moves:
            board.make_move(move)
            evaluation = -cls.alpha_beta_opt(board, cls.search_depth - 1, 0, beta, alpha)
            board.reverse_move()
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = move
            if cls.mate_found:
                return best_move
        
        return best_move


    @classmethod
    def alpha_beta_opt(cls, board: Board, depth: int, plies: int, alpha: int, beta: int):
        """
        Optimized alpha-beta search with more elaborate optimizations
        TODO: Transposition tables
        """
        if not depth:
            # return cls.quiescene(alpha, beta)
            return Evaluation.pst_shef(board)

        # if plies > 0:
        #     if cls.board.is_repetition():
        #         return 0
            # alpha = max(alpha, -cls.checkmate_value + plies)
            # beta = min(beta, cls.checkmate_value - plies)
            # if alpha >= beta:
            #     return alpha

        moves = order_moves(LegalMoveGenerator.load_moves(board), board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if board.is_terminal_state():
            status = board.get_status()
            if status:
                # Return checkmated value instead of negative infinity so the ai still chooses a move even if it only detects
                # checkmates, as the checkmate value still is better than the initial beta of -infinity
                return -cls.checkmate_value
            if status == 0: 
                return cls.draw

        for move in moves:
            # traversing down the tree
            board.make_move(move)
            evaluation = -cls.alpha_beta_opt(board, depth - 1, plies + 1, -beta, -alpha)
            board.reverse_move()

            # Move is even better than best eval before,
            # opponent won't choose this move anyway so PRUNE YESSIR
            if evaluation >= beta:
                # cls.cutoffs += 1
                return beta # Return -alpha of opponent, which will be turned to alpha in depth - 1
            # Keep track of best move for moving color
            alpha = max(evaluation, alpha)

        return alpha
        
    @classmethod
    def quiescene(cls, alpha, beta):
        """
        A dfs-like algorithm used for chess searches, only considering captureing moves, thus helping the conventional
        search with misjudgment of situations when significant captures could take place in a depth below the search depth.
        :return: the best evaluation of a particular game state, only considering captures
        """ 
        # Evaluate current position before doing any moves, so a potentially good state for non-capture moves
        # isn't ruined by bad captures
        # cls.evaluated_positions += 1
        eval = Evaluation.pst_shef()
        # Typical alpha beta operations
        if eval >= beta:
            return beta
        alpha = max(eval, alpha)

        moves = order_moves_pst(LegalMoveGenerator.load_moves(generate_quiets=False), cls.board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if cls.board.is_terminal_state():
            status = cls.board.get_status()
            if status:
                return -cls.checkmate_value
            if status == 0: 
                return cls.draw

        for move in moves:
            cls.board.make_move(move)
            evaluation = -cls.quiescene(-beta, -alpha)
            cls.board.reverse_move()
            # Move is even better than best eval before,
            # opponent won't choose move anyway so PRUNE YESSIR
            if evaluation >= beta:
                return beta
            # Keep track of best move for moving color
            alpha = max(evaluation, alpha)
        # If there are no captures to be done anymore, return the best evaluation
        return alpha


    @classmethod
    def minimax(cls, depth):
        """
        A brute force dfs-like algorithm traversing every node of the game's 
        possible-outcome-tree of given depth
        with branching factor b and depth d time-complexity is O(b^d)
        :return: best move possible
        """
        # leaf node, return the static evaluation of current board
        if not depth:
            return cls.board.shef()

        moves = LegalMoveGenerator.load_moves()
        
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        best_evaluation = float("-inf")
        for move in moves:
            cls.searched_nodes += 1
            cls.board.make_move(move)
            evaluation = -cls.minimax(depth - 1)
            best_evaluation = max(evaluation, best_evaluation)
            cls.board.reverse_move()

        return best_evaluation
    
    @classmethod
    def alpha_beta(cls, depth, alpha, beta):
        """
        Minimax with alpha-beta pruning
        """
        if not depth:
            return cls.board.shef()

        moves = LegalMoveGenerator.load_moves()
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        for move in moves:
            cls.searched_nodes += 1
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta(depth - 1, -beta, -alpha)
            cls.board.reverse_move()
            # Move is even better than best eval before,
            # opponent won't choose move anyway so PRUNE YESSIR
            if evaluation >= beta:
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
            board.make_move(move)
            evaluation = -cls.alpha_beta_opt(board, depth - 1, 0, beta, alpha)
            board.reverse_move()
            best_eval = max(evaluation, best_eval)
        return best_eval
            