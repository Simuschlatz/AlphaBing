from os import stat
from turtle import color
from piece import Piece
import numpy as np

class Board:
    def __init__(self, FEN: str, color_to_move: int) -> None:
        self.color_to_move = color_to_move
        self.opponent_color = 1 - color_to_move
        # Square-centric board repr
        self.squares = list(np.zeros(90, dtype=np.int16))
        self.moved_piece = None
        self.captured_piece = None
        self.previous_square = None
        self.moved_to = None
        # To keep track of the pieces' indices (Piece-centric repr)
        self.piece_lists = [[set() for i in range(7)] for i in range(2)]
        # DON'T EVER DO THIS IT TOOK ME AN HOUR TO FIX self.piece_list = [[set()] * 7] * 2 
        self.load_board_from_fen(FEN)


    @staticmethod
    def get_board_pos(mouse_pos, unit) -> tuple:
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        rank = int((mouse_y) // unit)
        file = int((mouse_x) // unit)
        rank = min(9, max(rank, 0))
        file = min(8, max(file, 0))
        return file, rank

    def switch_player_to_move(self):
        self.opponent_color = self.color_to_move
        self.color_to_move = 1 - self.color_to_move
        if self.color_to_move:
            print("RED MOVES")
            return
        print("WHITE MOVES")

    def load_board_from_fen(self, FEN: str) -> None:
        """Loads a board from Forsyth-Edwards-Notation (FEN)
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
                red = char.isupper()
                piece_type = Piece.letters.index(char.lower())
                self.piece_lists[red][piece_type].add(rank * 9 + file)
                self.squares[rank * 9 + file] = (int(red), piece_type)
                file += 1
            if char.isdigit():
                file += int(char)

    def load_fen_from_board(self) -> str:
        """:return: a Forsyth-Edwards-Notation (FEN) string from the current board
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
                is_red = piece[0]
                letter = Piece.letters[piece[1]].upper() if is_red else Piece.letters[piece[1]]
                fen += letter
            rank = i // 9
            file = i % 9
            if rank < 9 and file == 8 and empty_files_in_rank != 9:
                fen += "/"
                empty_files_in_rank = 0
            elif empty_files_in_rank == 9:
                fen += "9/"
                empty_files_in_rank = 0
        return fen

    def get_piece_list(self, piece_type: int, color_idx):
        return self.piece_lists[color_idx][piece_type]
    
    def is_friendly_square(self, square):
        piece = self.squares[square]
        return piece[0] == self.color_to_move if piece else False
    
    def is_square_empty(self, square):
        return not self.squares[square]

    @staticmethod
    def get_horse_block(current_square, target_square):
        d_rank = target_square // 9 - current_square // 9
        d_file = target_square % 9 - current_square % 9

        if abs(d_rank) > abs(d_file):
            return current_square + d_rank // 2 * 9
        return current_square + d_file // 2

    def make_human_move(self, current_square, target_square, piece) -> None:
        color_to_move, piece_type = piece
        # Updating piece lists
        self.piece_lists[color_to_move][piece_type].remove(current_square)  
        self.piece_lists[color_to_move][piece_type].add(target_square)

        self.captured_piece = self.squares[target_square]
        self.moved_piece = piece
        self.previous_square, self.moved_to = current_square, target_square

        for piece_list in self.piece_lists[1 - color_to_move]:
            piece_list.discard(target_square)
        # Moving the piece
        self.squares[target_square] = piece

        print(self.load_fen_from_board())
    def make_move(self, current_square, target_square, piece):
        color_to_move, piece_type = piece
        # Updating piece lists
        self.piece_lists[color_to_move][piece_type].remove(current_square)  
        self.piece_lists[color_to_move][piece_type].add(target_square)

        for piece_list in self.piece_lists[1 - color_to_move]:
            piece_list.discard(target_square)

        self.captured_piece = self.squares[target_square]
        self.moved_piece = piece
        self.previous_square, self.moved_to = current_square, target_square

        # Updating the board
        self.squares[target_square] = self.squares[current_square]
        self.squares[current_square] = 0

    def reverse_move(self):
        last_moved_color, piece_type = self.moved_piece

        self.piece_lists[last_moved_color][piece_type].remove(self.moved_to)  
        self.piece_lists[last_moved_color][piece_type].add(self.previous_square)

        if self.captured_piece:
            self.piece_lists[self.opponent_color][self.captured_piece[1]].add(self.moved_to)
        
        self.squares[self.previous_square] = self.moved_piece
        self.squares[self.moved_to] = self.captured_piece