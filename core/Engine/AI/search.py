"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from core.Engine.move_generator import LegalMoveGenerator
from core.Engine.board import Board
from core.Engine.AI.eval_utility import Evaluation
from core.Engine.AI import order_moves, order_moves_pst, Diagnostics
from core.Engine.piece import Piece


class Dfs:
    checkmate_value = 9999
    draw = 0
    positive_infinity = float("inf")
    negative_infinity = -positive_infinity

    @classmethod
    def init(cls, board: Board) -> None:
        cls.board = board
        cls.evaluated_positions = 0
        cls.cutoffs = 0

    @classmethod
    def search(cls, depth):
        """
        Starts traversal of board's possible configurations
        :return: best move possible
        """
        Diagnostics.init()
        best_move = None
        alpha = cls.positive_infinity
        beta = cls.negative_infinity
        best_eval = beta
        current_pos_moves = order_moves(LegalMoveGenerator.load_moves(), cls.board)
        cls.mate_found = False
        Diagnostics.depth = 0
        for move in current_pos_moves:
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta_opt(depth - 1, 0, beta, alpha)
            cls.board.reverse_move()
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = move
            # if cls.mate_found:
            #     return best_move
        return best_move
    
    @classmethod
    def get_best_eval(cls, depth):
        Diagnostics.init()
        alpha = cls.positive_infinity
        beta = cls.negative_infinity
        best_eval = beta
        current_pos_moves = order_moves(LegalMoveGenerator.load_moves(), cls.board)
        cls.abort_search = False
        for move in current_pos_moves:
            if cls.abort_search:
                return best_eval
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta_opt(depth - 1, 0, beta, alpha)
            cls.board.reverse_move()
            best_eval = max(evaluation, best_eval)
        return best_eval
            

    @classmethod
    def alpha_beta_opt(cls, depth, plies, alpha, beta):
        if not depth:
            Diagnostics.evaluated_nodes += 1
            return cls.quiescene(alpha, beta)

        # if plies > 0:
        #     if cls.board.is_repetition():
        #         return 0
            # alpha = max(alpha, -cls.checkmate_value + plies)
            # beta = min(beta, cls.checkmate_value - plies)
            # if alpha >= beta:
            #     return alpha

        moves = order_moves(LegalMoveGenerator.load_moves(), cls.board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if cls.board.is_terminal_state():
            status = cls.board.get_status()
            if status:
                # Return checkmated value instead of negative infinity so the ai still chooses a move even if it only detects
                # checkmates, as the checkmate value still is better than the initial beta of -infinity
                Diagnostics.best_eval = cls.checkmate_value
                return -cls.checkmate_value
            if status == 0: 
                return cls.draw

        for move in moves:
            # traversing down the tree
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta_opt(depth - 1, plies + 1, -beta, -alpha)
            cls.board.reverse_move()

            # Move is even better than best eval before,
            # opponent won't choose this move anyway so PRUNE YESSIR
            if evaluation >= beta:
                cls.cutoffs += 1
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
        cls.evaluated_positions += 1
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
                Diagnostics.best_eval = cls.checkmate_value
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

