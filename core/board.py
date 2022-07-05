from piece import Piece
import numpy as np

class Board:
    WIDTH = 691
    HEIGHT = 778
    initial_fen = "pheakaehp/9/1c5c/p1p1p1p1p/9/9/P1P1P1P1P/1C5C/9/PHEAKAEHP"
    UNIT = 78
    def __init__(self, FEN) -> None:
        self.squares = list(np.zeros(90, dtype=np.int16))
        # To keep track of the pieces' indices
        self.piece_square = [[], []]
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
    def is_out_of_bounds(self, index):
        return 0 > index > 89
        
    def load_board_from_fen(self, FEN) -> None:
        """Loads a board from Forsyth-Edwards-Notation (FEN)
        White: upper case
        Red: lower case
        King:K, Advisor:A, Elephant:E, Rook:R, Cannon:C, Horse:H, PAWN:P
        """
        file, rank = 0, 0
        for char in FEN:
            if char == "/":
                rank += 1
                file = 0
            if char.lower() in Piece.letters:
                white = char.isupper()
                piece = Piece.letters.index(char.lower())
                self.squares[rank * 9 + file] = (int(not white), piece)
                self.piece_square[not white].append(rank * 9 + file)
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
                letter = Piece.letters[piece[1]] if is_red else Piece.letters[piece[1]].upper()
                fen += letter
            rank = i // 9
            file = i % 9
            if rank != 9 and file == 8 and empty_files_in_rank != 9:
                fen += "/"
                empty_files_in_rank = 0
            elif empty_files_in_rank == 9:
                fen += "9/"
                empty_files_in_rank = 0
        return fen

    def make_move(self, selected_square, target_square, color_to_move, is_human_move=False, piece=None) -> None:
        self.piece_square[color_to_move].remove(selected_square)  
        self.piece_square[color_to_move].append(target_square)

        if target_square in self.piece_square[1 - color_to_move]:
            self.piece_square[1 - color_to_move].remove(target_square)

        if is_human_move:
            self.make_human_move(piece, target_square)
            return
        self.squares[target_square] = self.squares[selected_square]
        self.squares[selected_square] = 0

    def make_human_move(self, piece, target_square):
        self.squares[target_square] = piece