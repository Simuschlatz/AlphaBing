from piece import Piece

class Move_generator:
    # Orthogonal and diagonal offsets of board represented in one dimension
    dir_offsets = [-9, 1, 9, -1, -8, 10, 8, -10]
    def __init__(self, board) -> None:
        # Was too lazy counting the offsets by force, required to be in a specific order
        self.horse_jumps = self.jumps_from_orthogonal_offsets()
        self.dist_to_edge = self.precompute_dists()
        self.moves = set()
        self.illegal_moves = set()
        # Here you wouldn't have to add the -9, but it makes moves generation a lot easier
        self.horse_moves = self.precompute_horse_moves()
        self.board = board
        self.friendly = None
        self.target_squares = {}
        self.pinned_squares = []
        self.checkmate = False
        self.red_in_check = False
        self.white_in_check = False
        self.stalemate = False
        
    @staticmethod
    def precompute_dists() -> list:
        """
        :return: list of tuples containing the distances to the board's
        edges with orthogonal and diagonal movement for every square
        """
        distances = []
        for rank in range(10):
            for file in range(9):
                up = rank
                down = 9 - rank
                left = file
                right = 8 - file
                dist = [
                    up,
                    right,
                    down,
                    left,
                    min(up, right),
                    min(right, down),
                    min(down, left),
                    min(left, up)
                ]
                distances.append(dist)
        return distances

    @staticmethod
    def jumps_from_orthogonal_offsets():
        horse_offsets = []
        dir_offsets = Move_generator.dir_offsets[:4] + [-9]

        for dir_index in range(4):
            second_dir_idx = dir_index + 1

            for steps in range(2):
                first_dir_steps = 2 - steps
                second_dir_steps = 1 + steps
                new_offset = dir_offsets[dir_index] * first_dir_steps + dir_offsets[second_dir_idx] * second_dir_steps
                horse_offsets.append(new_offset)
        return horse_offsets

    def precompute_horse_moves(self) -> list:
        dir_offsets = Move_generator.dir_offsets[:4] + [-9]
        horse_moves = []
        for square in range(89):
            horse_moves.append([])
            for dir_index in range(8):
                target_square = square + self.horse_jumps[dir_index]
                target_rank = target_square // 9
                target_file = target_square - target_rank * 9
                current_rank = square // 9
                current_file = square - current_rank * 9
                max_difference = max(abs(current_rank - target_rank), abs(current_file - target_file))
                if max_difference > 2 or not -1 < target_square < 90:
                    continue
                horse_moves[square].append((square, target_square))

        return horse_moves

    def load_moves(self, color_to_move) -> list:
        """
        :return: a tuple containing the start and end indices of all possible moves
        color_to_move : int
        """
        # variable "color_to_move" can be used for indexing and determining the color of piece 
        # (see "piece.py > class Piece") here e.g. allows to only loop over friendly indices
        self.friendly = color_to_move

        self.moves = set()
        self.illegal_moves = set()
        self.target_squares = {}

        for square in self.board.piece_square[self.friendly]:
            piece_type = self.board.squares[square][1]
            
            if piece_type == Piece.rook:
                self.generate_sliding_moves(square, False)
            if piece_type == Piece.cannon:
                self.generate_sliding_moves(square, True)
            if piece_type == Piece.horse:
                self.generate_horse_moves(square)
            # if piece_type == Piece.king:
            #     self.generate_king_moves()
        print(self.moves)
        return self.moves

    def generate_king_moves():
        pass

    def generate_cannon_moves(self, square):
        pass

    def generate_diagonal_moves():
        pass

    def generate_horse_moves(self, current_square):
        legal_moves = self.horse_moves[current_square]
        illegal_moves = set()

        for dir_idx in range(4):
            if self.dist_to_edge[current_square][dir_idx] < 1:
                continue

            blocking_square = current_square + self.dir_offsets[dir_idx]
            is_blocking_move = self.board.squares[blocking_square]
            if is_blocking_move:
                blocked_squares = [current_square + self.horse_jumps[dir_idx * 2 - i] for i in range(2)]

                illegal_moves.add((current_square, blocked_squares[0]))
                illegal_moves.add((current_square, blocked_squares[1]))
        legal_moves = list(set(legal_moves) - illegal_moves)
        # legal_moves = list(filter(lambda move: move in illegal_moves, legal_moves))


        for move in legal_moves:
            target_square = move[1]
            print(target_square)
            if self.board.squares[target_square]:
                target_piece = self.board.squares[target_square]
                if target_piece[0] == self.friendly:
                    continue

            self.moves.add((current_square, target_square))
            self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                
    def generate_sliding_moves(self, current_square, is_cannon):
        # Going through chosen direction indices
        for dir_index in range(4):
            piece_along_ray = False
            # "Walking" in direction using direction offsets
            for step in range(self.dist_to_edge[current_square][dir_index]):
                target_square = current_square + Move_generator.dir_offsets[dir_index] * (step + 1)
                target_piece = False

                if piece_along_ray:
                    if not self.board.squares[target_square]:
                        continue
                    target_piece = self.board.squares[target_square]
                    if target_piece[0] == self.friendly:
                        continue
                        
                elif self.board.squares[target_square]:
                    if is_cannon:
                        piece_along_ray = True
                        continue

                    target_piece = self.board.squares[target_square]
                    if target_piece[0] == self.friendly:
                        break

                self.moves.add((current_square, target_square))
                self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]

                # If piece on target square and not friendly, go to next direction
                if target_piece:
                    break