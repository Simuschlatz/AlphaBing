from core.engine.piece import Piece 
from core.engine.zobrist_hashing import ZobristHashing
import numpy as np
from collections import deque
from logging import getLogger
logger = getLogger(__name__)

class Board:
    max_plies = 60

    def __init__(self, FEN: str, play_as_red=True) -> None:
        """
        :param FEN: Forsyth-Edwards-Notation, a concise string version to represent a state of game
        """
        # Square-centric board repr
        self.squares = list(np.zeros(90, dtype=np.int8))
        # NOTE: the bitboards aren't continually updated in make_move() or reverse_move()
        self.bitboards = np.zeros((2, 7, 90), dtype=np.int8)
        # To keep track of the pieces' indices (Piece-centric repr)
        # Piece list at index 0 keeps track of pieces at the top, index 1 for bottom
        self.piece_lists = [[[] for _ in range(7)] for _ in range(2)]
        # which color moves first - boolean "is_red_first" or "is_red" can be used interchangeably 
        # with int "color_to_start" or "color" because the colors are represented as ints in [0, 1]
        self.fullmoves, self.plies = 0, 0
        # basic setup
        is_red_first = self.load_board_from_fen(FEN)
        # Bitboards 2x7x10x9 (each side, number of pieces, board dims)
        self.moving_side = int(play_as_red == is_red_first)
        self.opponent_side = 1 - self.moving_side
        self.moving_color = int(is_red_first)
        self.opponent_color = 1 - self.moving_color
        # If we don't play as red, the pieces are at the top, 
        self.is_red_up = not play_as_red
        # -> is_red_up xor moving_color = moving side
        self.bitboards = self.piecelist_to_bitboard(adjust_perspective=True)
        # moving color is 16 if red moves first or 8 when white moves first
        # self.moving_color = (1 + red_moves_first) * 8
        # self.opponent_color = (2 - red_moves_first) * 8
        # int is added each time a pawn is moved to know the previous ply count when reversing a move
        self.plies_history = deque()
        # This keeps track of all game states in history, 
        # so multiple moves can be reversed consecutively, coming in really handy in dfs
        self.game_history = deque() # Stack(:previous square, :target square :captured piece)
        # DON'T EVER DO THIS IT TOOK ME AN HOUR TO FIX: self.piece_list = [[set()] * 7] * 2 
        self.zobrist_key = ZobristHashing.digest(self.moving_side, self.piece_lists)
        self.repetition_history = {self.zobrist_key: 1}

    @staticmethod
    def get_file_and_rank(square: int):
        return square % 9, square // 9
    
    @staticmethod
    def get_fr_d(square_1: int, square_2: int):
        """
        :return: distance between two squares in files and ranks 
        from square_1's perspective
        """
        d = square_2 - square_1
        return d % 9, d // 9
    
    @staticmethod
    def get_square(file: int, rank: int):
        return rank * 9 + file

    def switch_moving_color(self):
        self.opponent_color = self.moving_color
        self.moving_color = 1 - self.moving_color
        self.opponent_side = self.moving_side
        self.moving_side = 1 - self.moving_side

    def load_board_from_fen(self, FEN: str) -> None:
        """
        Loads a board from Forsyth-Edwards-Notation (FEN)
        Black: upper case
        Red: lower case
        King:K, Advisor:A, Elephant:E, Rook:R, Cannon:C, Horse:H, Pawn:P
        """
        file, rank = 0, 0
        board_config, color, *_, plies, fullmoves = FEN.split()
        self.plies, self.fullmoves = map(int, (plies, fullmoves))
        # print("plies: ", self.plies, "fullmoves: ", self.fullmoves)
        moving_color = color == "w"
        for char in board_config:
            if char == "/":
                rank += 1
                file = 0
            if char.lower() in Piece.letters:
                color = int(char.isupper())
                piece_type = Piece.letters.index(char.lower())
                # If red is playing the top side, its pieces are stored in piece list index 0
                self.piece_lists[color][piece_type].append(rank * 9 + file)
                # self.squares[rank * 9 + file] = (is_red + 1) * 8 + piece_type
                self.squares[rank * 9 + file] = (color, piece_type)
                file += 1
            if char.isdigit():
                file += int(char)
        return moving_color

    def load_fen_from_board(self) -> str:
        """
        :return: a Forsyth-Edwards-Notation (FEN) string from the current board
        """
        config = ""
        empty_files_in_rank = 0
        for i, piece in enumerate(self.squares):
            if not piece:
                empty_files_in_rank += 1
            else:
                if empty_files_in_rank:
                    config += str(empty_files_in_rank)
                    empty_files_in_rank = 0
                color, piece_type = piece
                letter = Piece.letters[color * 7 + piece_type]
                config += letter
            file, rank = self.get_file_and_rank(i)
            if empty_files_in_rank == 9:
                config += "9"
                empty_files_in_rank = 0
            if rank < 9 and file == 8:
                config += "/"
                empty_files_in_rank = 0
        color = Piece.colors[self.moving_color]
        fen = " ".join([config, color, "- -", str(self.plies), str(self.fullmoves)])
        return fen

    def get_piece_list(self, color: int, piece_type: int):
        return self.piece_lists[color][piece_type - 1]
    
    def is_capture(self, square: int):
        return self.squares[square]

    def is_terminal_state(self, num_moves: int):
        """
        :return: if current position is a terminal state
        """
        return not num_moves or self.plies >= self.max_plies


    def get_terminal_status(self, num_moves: int):
        if num_moves and self.plies < self.max_plies: return -1
        if not num_moves: return 1
        return 0
        # return not num_moves, self.plies >= self.max_plies
            
    @staticmethod
    def get_abs_dist(square_1: int, square_2: int):
        """
        :return: absolute distance between two squares in each axis (dcolumns, drows)
        """
        dist_x = abs(square_1 % 9 - square_2 % 9)
        dist_y = abs(square_1 // 9 - square_2 // 9)
        return dist_x, dist_y

    @staticmethod
    def get_manhattan_dist(square_1: int, square_2: int):
        """
        :return: manhattan distance between two squares in each axis (dcolumns, drows)
        """
        dist_x = abs(square_1 % 9 - square_2 % 9)
        dist_y = abs(square_1 // 9 - square_2 // 9)
        return dist_x + dist_y

    @staticmethod
    def get_dists(square_1: int, square_2: int):
        """
        :return: x- and y-distance between two squares in each axis (dcolumns, drows)
        """
        dist_x = int(square_1 % 9 - square_2 % 9)
        dist_y = square_1 // 9 - square_2 // 9
        return dist_x, dist_y

    def lazo_update(self, moved_piece_type: int, captured_piece: tuple, moved_from: int, moved_to: int):
        """
        Lazy zobrist, modifies exisiting zobrist key instead of creating a new one
        """
        if captured_piece:
            cap_piece_type = Piece.get_type(captured_piece)
            self.zobrist_key ^= ZobristHashing.table[self.opponent_side][cap_piece_type][moved_to]
        self.zobrist_key ^= ZobristHashing.table[self.moving_side][moved_piece_type][moved_from]
        self.zobrist_key ^= ZobristHashing.table[self.moving_side][moved_piece_type][moved_to]
        self.zobrist_key ^= self.opponent_side
        self.zobrist_key ^= self.moving_side

    @staticmethod
    def flip_move(move):
        return 89 - move[0], 89 - move[1]

    @staticmethod
    def flip_moves(moves): 
        return [(89 - move[0], 89 - move[1]) for move in moves]

    def piecelist_to_bitboard(self, adjust_perspective=True):
        """
        :param adjust_perspective: if True, each side's bitboards are adjusted to 
        that side's perspective and the two sides' bitboard planes are occasionally
        swapped so that the first set of planes is always that of the moving side
        :return: array of two sets of 7 bitboards generated from piece lists
        """
        bitboards = np.zeros((2, 7, 90), dtype=np.float32)
        for color, piece_lists in enumerate(self.piece_lists):
            # determines whether the squares have to be adjusted
            flip = color != self.is_red_up and adjust_perspective

            for piece_type, squares in enumerate(piece_lists):
                # adjust the squares to current side's perspective
                if flip: squares = [89 - square for square in squares]
                np.put(bitboards[color][piece_type], squares, 1)
        # put the moving side's board first (only needs adjustment if lower side is moving)
        if self.moving_color != self.is_red_up and adjust_perspective: bitboards = np.flipud(bitboards)        
        return bitboards

    @staticmethod
    def mirror_bitboard(bitboards, axis=2):
        """
        :param bitboards: bitboard of current state, 3-dimensional array
        :param axis: 0 for mirroring along x-axis (vertical mirroring), 2 for horizontal mirroring
        """
        return np.flip(bitboards, axis)

    @staticmethod
    def mirror_move(move: tuple):
        start, target = move
        start_file, start_rank = Board.get_file_and_rank(start)
        target_file, target_rank = Board.get_file_and_rank(target)

        mirrored_start = start_rank * 9 + 8 - start_file
        mirrored_target = target_rank * 9 + 8 - target_file

        return (mirrored_start, mirrored_target)

    def is_repetition(self):
        return self.zobrist_key in self.repetition_history
    
    def make_move(self, move: tuple, search_state=False):
        moved_from, moved_to = move
        moved_piece = self.squares[moved_from]
        piece_type = Piece.get_type_no_check(moved_piece)
        # Updating piece lists
        self.piece_lists[self.moving_color][piece_type].remove(moved_from)
        self.piece_lists[self.moving_color][piece_type].append(moved_to)
        
        captured_piece = self.squares[moved_to]
        if captured_piece:
            captured_type = Piece.get_type_no_check(captured_piece)
            self.piece_lists[self.opponent_color][captured_type].remove(moved_to)

        if self.moving_color == Piece.black:
            self.fullmoves += 1
        if piece_type == Piece.pawn:
            self.plies_history.append(self.plies)
            self.plies = 0
        else: self.plies += 1

        # Adding current game state to history
        current_game_state = (*move, captured_piece)
        self.game_history.append(current_game_state)
        # Updating the board
        self.squares[moved_to] = moved_piece
        self.squares[moved_from] = 0

        # Update zobrist key
        self.lazo_update(piece_type, captured_piece, *move)
        if not search_state:
            self.repetition_history[self.zobrist_key] = self.repetition_history.get(self.zobrist_key, 0) + 1
            # print(self.repetition_history)
        # print(self.zobrist_key)

        self.switch_moving_color()
        # self.piecelist_to_bitboard(adjust_perspective=True)
        # Used for quiescene search
        return bool(captured_piece)
        
    def reverse_move(self, search_state=False):
        # Accessing the previous game state data
        previous_square, moved_to, captured_piece = self.game_history.pop()

        moved_piece = self.squares[moved_to]
        piece_type = Piece.get_type_no_check(moved_piece)

        # Reversing the move
        self.piece_lists[self.opponent_color][piece_type].remove(moved_to)  
        self.piece_lists[self.opponent_color][piece_type].append(previous_square)

        if captured_piece:
            captured_type = Piece.get_type_no_check(captured_piece)
            self.piece_lists[self.moving_color][captured_type].append(moved_to)

        self.squares[previous_square] = moved_piece
        self.squares[moved_to] = captured_piece

        # Switch back to previous moving color
        self.switch_moving_color()
        if self.moving_color == Piece.black: self.fullmoves -= 1
        self.plies = self.plies_history.pop() if piece_type == Piece.pawn else self.plies - 1

        # Update Zobrist key, as moving side is switched the same method can be used for reversing the zobrist changes
        if not search_state:
            if self.repetition_history[self.zobrist_key] == 1:
                del self.repetition_history[self.zobrist_key]
            else:
                self.repetition_history[self.zobrist_key] -= 1
            # logger.info(self.repetition_history)
        self.lazo_update(piece_type, captured_piece, previous_square, moved_to)

        #     return 
        # print(self.zobrist_key)

    def get_previous_configs(self, depth: int):
        depth = min(len(self.game_history), depth)
        print(f"depth: {depth}")
        prefix = "----"
        for i in range(1, depth):
            print(self.game_history)
            previous_square, moved_to, _ = list(self.game_history)[-1]
            self.reverse_move()
            # move_str = self.get_move_notation((previous_square, moved_to)) + "  "
            fen = self.load_fen_from_board()
            msg = prefix + fen + prefix
            depth_info = f" depth: {i} "
            len_header_prefix = (len(msg) - len(depth_info)) // 2
            header_prefix = "-" * len_header_prefix
            header = header_prefix + depth_info + header_prefix
            separation = "-" * len(msg)
            # print(header)
            print(msg)
            # print(separation)

    def get_move_notation(self, move: tuple):
        former_square, new_square = move
        former_rank, former_file = self.get_file_and_rank(former_square)
        new_rank, new_file = self.get_file_and_rank(new_square)
        piece = self.squares[former_square]
        color, piece_type = piece
        letter = Piece.letters[color * 7 + piece_type]
        return f"{letter}({former_rank}{former_file})-{new_rank}{new_file}"