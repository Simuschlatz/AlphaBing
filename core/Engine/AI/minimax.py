from Engine.move_generator import Legal_move_generator

class Dfs:
    def __init__(self, board) -> None:
        self.board = board
        self.traversed_nodes = 0

    def traverse_tree(self, depth):
        """
        Starts traversal of board's possible configurations
        :return: best move possible
        """
        best_move = None
        positive_infinity = float("inf")
        negative_infinity = float("-inf")
        best_eval = negative_infinity
        current_pos_moves = Legal_move_generator.load_moves(self.board)
        for move in current_pos_moves:
            self.board.make_move(move)
            evaluation = -self.minimax_alpha_beta(depth, negative_infinity, positive_infinity)
            # evaluation = - self.minimax(depth)
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = move
            self.board.reverse_move()
        print("BEST EVAL: ", best_eval)
        return best_move


    def minimax(self, depth):
        """
        A brute force dfs-like algorithm traversing every node of the game's 
        possible-outcome-tree of given depth
        with branching factor b and depth d time-complexity is O(b^d)
        :return: best move possible
        """
        # leaf node, return the static evaluation of current board
        if not depth:
            return self.board.shef()

        moves = Legal_move_generator.load_moves(self.board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        best_evaluation = float("-inf")
        for move in moves:
            self.board.make_move(move)
            evaluation = -self.minimax(depth - 1)
            best_evaluation = max(evaluation, best_evaluation)
            self.board.reverse_move()

        return best_evaluation
    
    def minimax_alpha_beta(self, depth, alpha, beta):
        if not depth:
            return self.board.shef()

        moves = Legal_move_generator.load_moves(self.board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        for move in moves:
            self.board.make_move(move)
            evaluation = -self.minimax_alpha_beta(depth - 1, -beta, -alpha)
            self.board.reverse_move()
            if evaluation >= beta:
                return beta
            alpha = max(evaluation, alpha)
        return alpha

        
        
    