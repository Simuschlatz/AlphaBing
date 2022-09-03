from core.Engine import piece
from core.Engine.piece import Piece
from core.Engine.zobrist_hashing import Zobrist_hashing
import numpy as np
from collections import deque

class Board:
    # Piece's values
    king = float("inf")
    pawn = 10
    advisor = 20
    elephant = 20
    horse = 40
    cannon = 45
    rook = 100
    values = (0, elephant, advisor, cannon, pawn, rook, horse)

    def __init__(self, FEN: str, play_as_red: int, red_moves_first=True) -> None:
        # Look core/notes.md
        self.moving_side = int(not(play_as_red != red_moves_first))
        self.opponent_side = 1 - self.moving_side
        # If we don't play as red, the pieces are at the top, 
        self.is_red_up = not play_as_red
        # moving color is 16 if red moves first or 8 when white moves first
        self.moving_color = (1 + red_moves_first) * 8
        self.opponent_color = (2 - red_moves_first) * 8

        # Square-centric board repr
        self.squares = list(np.zeros(90, dtype=np.int8))
        # This keeps track of all game states in history, 
        # so multiple moves can be reversed consecutively, coming in really handy in dfs
        self.game_history = deque() # Stack(:previous square, :target square :captured piece)
        # To keep track of the pieces' indices (Piece-centric repr)
        # Piece list at index 0 keeps track of pieces at the top, index 1 for bottom
        self.piece_lists = [[set() for _ in range(7)] for _ in range(2)]
        # DON'T EVER DO THIS IT TOOK ME AN HOUR TO FIX: self.piece_list = [[set()] * 7] * 2 
        self.load_board_from_fen(FEN)
        self.zobrist_key = Zobrist_hashing.get_zobrist_key(self.moving_side, self.piece_lists)
        self.repetition_history = deque([self.zobrist_key])

    @staticmethod
    def get_file_and_rank(square):
        return square % 9, square // 9
    
    @staticmethod
    def get_square(file, rank):
        return rank * 9 + file

    def switch_moving_side(self):
        self.opponent_side = self.moving_side
        self.moving_side = 1 - self.moving_side
        temp = self.moving_color
        self.moving_color = self.opponent_color
        self.opponent_color = temp

    def load_board_from_fen(self, FEN: str) -> None:
        """
        Loads a board from Forsyth-Edwards-Notation (FEN)
        Black: upper case
        Red: lower case
        King:K, Advisor:A, Elephant:E, Rook:R, Cannon:C, Horse:H, Pawn:P
        """
        file, rank = 0, 0
        for char in FEN:
            if char == "/":
                rank += 1
                file = 0
            if char.lower() in Piece.letters:
                is_red = char.isupper()
                piece_type = Piece.letters.index(char.lower())
                # If red is playing the top side
                self.piece_lists[is_red - self.is_red_up][piece_type].add(rank * 9 + file)
                self.squares[rank * 9 + file] = (is_red + 1) * 8 + piece_type
                file += 1
            if char.isdigit():
                file += int(char)

    def load_fen_from_board(self) -> str:
        """
        :return: a Forsyth-Edwards-Notation (FEN) string from the current board
        """
        fen = ""
        empty_files_in_rank = 0
        for i, piece in enumerate(self.squares):
            if not piece:
                empty_files_in_rank += 1
            else:
                if empty_files_in_rank:
                    fen += str(empty_files_in_rank)
                    empty_files_in_rank = 0
                is_red = Piece.is_color(piece, Piece.red)
                piece_type = Piece.get_type(piece)
                letter = Piece.letters[is_red * 7 + piece_type]
                fen += letter
            file, rank = self.get_file_and_rank(i)
            if rank < 9 and file == 8 and empty_files_in_rank != 9:
                fen += "/"
                empty_files_in_rank = 0
            elif empty_files_in_rank == 9:
                fen += "9/"
                empty_files_in_rank = 0
        return fen

    def get_piece_list(self, color_idx, piece_type: int):
        return self.piece_lists[color_idx][piece_type]
    
    def is_capture(self, square):
        return self.squares[square]

    @staticmethod
    def get_manhattan_dist(square_1, square_2):
        """
        :return: manhattan distance between two squares on a collapsed 9 x 10 grid
        """
        dist_x = abs(square_1 % 9 - square_2 % 9)
        dist_y = abs(square_1 // 9 - square_2 // 9)
        return dist_x + dist_y

    @staticmethod
    def get_dists(square_1, square_2):
        """
        :return: x- and y-distance between two squares on a collapsed 9 x 10 grid
        """
        dist_x = int(square_1 % 9 - square_2 % 9)
        dist_y = square_1 // 9 - square_2 // 9
        return dist_x, dist_y

    def update_zobrist(self, moved_piece_type, captured_piece, moved_from, moved_to):
        if captured_piece:
            cap_piece_type = Piece.get_type(captured_piece)
            self.zobrist_key ^= Zobrist_hashing.table[self.opponent_side][cap_piece_type][moved_to]
        self.zobrist_key ^= Zobrist_hashing.table[self.moving_side][moved_piece_type][moved_from]
        self.zobrist_key ^= Zobrist_hashing.table[self.moving_side][moved_piece_type][moved_to]
        self.zobrist_key ^= self.opponent_side
        self.zobrist_key ^= self.moving_side

    def make_move(self, move, search_state=True):
        moved_from, moved_to = move
        moved_piece = self.squares[moved_from]
        piece_type = Piece.get_type(moved_piece)
        # Updating piece lists
        self.piece_lists[self.moving_side][piece_type].remove(moved_from)
        self.piece_lists[self.moving_side][piece_type].add(moved_to)
        
        captured_piece = self.squares[moved_to]
        if captured_piece:
            captured_type = Piece.get_type(captured_piece)
            self.piece_lists[self.opponent_side][captured_type].remove(moved_to)

        # Adding current game state to history
        current_game_state = (moved_from, moved_to, captured_piece)
        self.game_history.append(current_game_state)
        # Updating the board
        self.squares[moved_to] = moved_piece
        self.squares[moved_from] = 0
        # Update zobrist key
        self.update_zobrist(piece_type, captured_piece, *move)
        # print(self.zobrist_key)
        self.switch_moving_side()

        # self.zobrist_key = Zobrist_hashing.get_zobrist_key(self.moving_side, self.piece_lists)
        # Used for quiescene search
        return bool(captured_piece)
        
    def reverse_move(self):
        if not len(self.game_history):
            return
        # Accessing the previous game state data
        previous_square, moved_to, captured_piece = self.game_history.pop()

        moved_piece = self.squares[moved_to]
        piece_type = Piece.get_type(moved_piece)

        # Reversing the move
        self.piece_lists[self.opponent_side][piece_type].remove(moved_to)  
        self.piece_lists[self.opponent_side][piece_type].add(previous_square)

        if captured_piece:
            captured_type = Piece.get_type(captured_piece)
            self.piece_lists[self.moving_side][captured_type].add(moved_to)

        self.squares[previous_square] = moved_piece
        self.squares[moved_to] = captured_piece

        # Switch back to previous moving color
        self.switch_moving_side()
        # Update Zobrist key, as moving side is switched the same method can be used for reversing the zobrist changes
        self.update_zobrist(piece_type, captured_piece, previous_square, moved_to)
        # print(self.zobrist_key)

    def get_previous_configs(self, depth):
        depth = min(len(self.game_history), depth)
        prefix = "----"
        for i in range(depth):
            self.reverse_move()
            fen = self.load_fen_from_board()
            msg = prefix + fen + prefix
            depth_info = f" depth: {i} "
            len_header_prefix = (len(msg) - len(depth_info)) // 2
            header_prefix = "-" * len_header_prefix
            header = header_prefix + depth_info + header_prefix
            separation = "-" * len(msg)
            print(header)
            print(msg)
            print(separation)

    def get_move_notation(self, move):
        former_square, new_square = move
        former_rank, former_file = self.get_file_and_rank(former_square)
        new_rank, new_file = self.get_file_and_rank(new_square)
        piece = self.squares[former_square]
        is_red = Piece.is_color(piece, Piece.red)
        piece_type = Piece.get_type(piece)
        letter = Piece.letters[is_red * 7 + piece_type]
        return (f"{letter}({former_rank}{former_file})-{new_rank}{new_file}")