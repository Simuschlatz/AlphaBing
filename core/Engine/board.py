from Engine.piece import Piece
import numpy as np
# from collections import deque

class Board:
    king = float("inf")
    pawn = 1
    advisor = 2
    elephant = 2
    horse = 4
    cannon = 4.5
    rook = 10
    values = (king, elephant, advisor, cannon, pawn, rook, horse)

    def __init__(self, FEN: str, moving_color: int) -> None:
        self.moving_color = moving_color
        self.opponent_color = 1 - moving_color
        # Square-centric board repr
        self.squares = list(np.zeros(90, dtype=np.int8))
        # This keeps track of all game states in history, 
        # so multiple moves can be reversed consecutively, coming in really handy in dfs
        self.game_history = [] # Stack(: sqprevuare, :target square :captured piece)
        # self.game_history = deque()

        # To keep track of the pieces' indices (Piece-centric repr)
        self.piece_lists = [[set() for _ in range(7)] for _ in range(2)]
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

    def switch_moving_color(self):
        self.opponent_color = self.moving_color
        self.moving_color = 1 - self.moving_color
        # if self.moving_color:
        #     print("RED MOVES")
        #     return
        # print("WHITE MOVES")

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
                color = char.isupper()
                piece_type = Piece.letters.index(char.lower())
                self.piece_lists[color][piece_type].add(rank * 9 + file)
                self.squares[rank * 9 + file] = (int(color), piece_type)
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
                is_red, piece_type = piece
                letter = Piece.letters[is_red * 7 + piece_type]
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
    
    def is_capture(self, square):
        return self.squares[square]

    # def is_blocking_check(check_piece):

    @staticmethod
    def get_horse_block(current_square, target_square):
        d_rank = target_square // 9 - current_square // 9
        d_file = target_square % 9 - current_square % 9

        if abs(d_rank) > abs(d_file):
            return current_square + d_rank // 2 * 9
        return current_square + d_file // 2

    def make_move(self, move):
        previous_square, moved_to = move
        moved_piece = self.squares[previous_square]
        _, piece_type = moved_piece
        # Updating piece lists
        self.piece_lists[self.moving_color][piece_type].remove(previous_square)
        self.piece_lists[self.moving_color][piece_type].add(moved_to)
        
        captured_piece = self.squares[moved_to]
        is_capture = bool(captured_piece)
        if is_capture:
            captured_type = captured_piece[1]
            self.piece_lists[self.opponent_color][captured_type].remove(moved_to)

        # Adding current game state to history
        current_game_state = (previous_square, moved_to, captured_piece)
        self.game_history.append(current_game_state)
        # Updating the board
        self.squares[moved_to] = moved_piece
        self.squares[previous_square] = 0
        self.switch_moving_color()
        # print(self.load_fen_from_board())

        # Used for quiescene search
        return is_capture
        
    def reverse_move(self):
        if not len(self.game_history):
            return
        # Accessing the previous game state data
        previous_square, moved_to, captured_piece = self.game_history.pop()

        moved_piece = self.squares[moved_to]
        color, piece_type = moved_piece

        # Reversing the move
        self.piece_lists[color][piece_type].remove(moved_to)  
        self.piece_lists[color][piece_type].add(previous_square)

        if captured_piece:
            captured_type = captured_piece[1]
            self.piece_lists[1 - color][captured_type].add(moved_to)

        self.squares[previous_square] = moved_piece
        self.squares[moved_to] = captured_piece

        # Switch back to previous moving color
        self.switch_moving_color()


    def get_move_notation(self, move):
        former_square, new_square = move
        former_rank, former_file = former_square // 9, former_square % 9
        new_rank, new_file = new_square // 9, new_square % 9
        color, piece_type = self.squares[former_square]
        letter = Piece.letters[color * 7 + piece_type]
        return (f"{letter}({former_rank}{former_file})-{new_rank}{new_file}")


    def shef(self):
        """
        Standard Heuristic Evaluation Function: \n
        :return: a heuristic evaluation of current material on board relative to moving color.
        positive: good
        negative: bad
        """
        friendly_eval = self.static_material_eval(self.moving_color)
        opponent_eval = self.static_material_eval(self.opponent_color)
        return friendly_eval - opponent_eval
    
    def static_material_eval(self, color):
        material = 0
        for piece_id in range(1, 7):
            material += len(self.piece_lists[color][piece_id]) * self.values[piece_id]
        return material