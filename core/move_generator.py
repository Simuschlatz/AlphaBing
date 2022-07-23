from piece import Piece
from precomputed_move_maps import Precomputing_moves
class Legal_move_generator:
    
    def __init__(self, board) -> None:
        Precomputing_moves.init_constants()
        self.dir_offsets = Precomputing_moves.dir_offsets
        self.dist_to_edge = Precomputing_moves.dist_to_edge

        # Precalculating move maps
        self.king_moves = Precomputing_moves.precompute_king_moves()
        self.rook_moves = Precomputing_moves.precompute_rook_moves()
        self.horse_moves = Precomputing_moves.precompute_horse_moves()
        self.advisor_moves = Precomputing_moves.precompute_advisor_moves()
        self.elephant_moves = Precomputing_moves.precompute_elephant_moves()
        self.pawn_moves = Precomputing_moves.precompute_pawn_moves()

        self.board = board


    def load_moves(self) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible moves
        color_to_move : int
        """
        self.init()
        self.calculate_attack_data()
        self.generate_king_moves()
        # In a double check, only the king can move
        if self.double_check: return self.moves
        self.generate_rook_moves()
        self.generate_cannon_moves()
        self.generate_horse_moves()
        self.generate_advisor_moves()
        self.generate_pawn_moves()
        self.generate_elephant_moves()

        return self.moves
    

    def init(self):
        # variable "color_to_move" can be used for indexing and determining the color of piece 
        # (see "piece.py > class Piece") here e.g. allows to only loop over friendly indices
        self.friendly = self.board.color_to_move
        self.opponent = 1 - self.friendly
        self.friendly_king = list(self.board.piece_lists[self.friendly][Piece.king]).pop()
        self.opponent_king = list(self.board.piece_lists[self.opponent][Piece.king]).pop()
        self.flying_general_possibility = self.friendly_king % 9 == self.opponent_king % 9

        self.moves = set()
        self.target_squares = {}

        self.attack_map = set()
        self.horse_attack_map = set()
        self.rook_attack_map = set()
        self.cannon_attack_map = set()
        self.pawn_attack_map = set()
        self.king_attack_map = set()

        self.pinned_squares = set()
        self.double_pinned = set()
        self.check = False
        self.double_check = False


    def generate_king_moves(self) -> None:
        current_square = self.friendly_king

        target_squares = self.king_moves[self.friendly][current_square]
        for target_square in target_squares:
            if target_square in self.attack_map:
                continue
            target_piece = self.board.squares[target_square]
            if Piece.is_color(target_piece, self.friendly):
                continue
            self.moves.add((current_square, target_square))
            self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]


    def generate_pawn_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal pawn moves
        """
        # Looping over friendly pawns
        for current_square in self.board.piece_lists[self.friendly][Piece.pawn]:
            target_squares = self.pawn_moves[self.friendly][current_square]
            for target_square in target_squares:
                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue

                self.moves.add((current_square, target_square))
                self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]


    def generate_elephant_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal elephant moves
        """
        for elephant_square in self.board.piece_lists[self.friendly][Piece.elephant]:
            target_squares = self.elephant_moves[self.friendly][elephant_square]
            illegal_squares = set()
            for dir_idx in range(4, 8):
                # Checking for blocks
                if self.dist_to_edge[elephant_square][dir_idx] < 1:
                    continue

                offset = self.dir_offsets[dir_idx]
                blocking_square = elephant_square + offset

                if self.board.squares[blocking_square]:
                    illegal_squares.add(elephant_square + offset * 2)

            # Removing illegal target squares
            target_squares = list(set(target_squares) - illegal_squares)
            
            for target_square in target_squares:
                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue
                
                self.moves.add((elephant_square, target_square))
                self.target_squares[elephant_square] = self.target_squares.get(elephant_square, []) + [target_square]


    def generate_advisor_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal advisor moves
        """
        for advisor_square in self.board.piece_lists[self.friendly][Piece.advisor]:
            target_squares = self.advisor_moves[self.friendly][advisor_square]
            
            for target_square in target_squares:
                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue

                self.moves.add((advisor_square, target_square))
                self.target_squares[advisor_square] = self.target_squares.get(advisor_square, []) + [target_square]


    def generate_horse_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal horse moves
        """
        horse_offsets = self.dir_offsets[8:16]

        for horse_square in self.board.piece_lists[self.friendly][Piece.horse]:
            legal_moves = self.horse_moves[horse_square]
            illegal_moves = set()

            # removing moves blocked by other pieces
            for dir_idx in range(4):
                if self.dist_to_edge[horse_square][dir_idx] < 1:
                    continue

                blocking_square = horse_square + self.dir_offsets[dir_idx]
                is_blocking_move = self.board.squares[blocking_square]
                if is_blocking_move:

                    # make use of the order of horse_jumps
                    # use the dir_idx for calculating the blocking square to also get the moves blocked by it
                    blocked_squares = [horse_square + horse_offsets[dir_idx * 2 - i] for i in range(2)]
                    illegal_moves.add((horse_square, blocked_squares[0]))
                    illegal_moves.add((horse_square, blocked_squares[1]))

            legal_moves = list(set(legal_moves) - illegal_moves)
            # legal_moves = list(filter(lambda move: move in illegal_moves, legal_moves))
            for move in legal_moves:
                target_square = move[1]
                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue

                self.moves.add((horse_square, target_square))
                self.target_squares[horse_square] = self.target_squares.get(horse_square, []) + [target_square]


    def generate_rook_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal rook moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.rook]:
            rook_attack_map = self.rook_moves[current_square]
            # Going through chosen direction indices
            for target_in_dir in rook_attack_map.values():
                target_piece = False
                # "Walking" in direction using direction offsets
                for rook_square in target_in_dir:
                    target_piece = self.board.squares[rook_square]
                    # If target_piece is friendly, go to next direction
                    if Piece.is_color(target_piece, self.friendly):
                        break

                    self.moves.add((current_square, rook_square))
                    self.target_squares[current_square] = self.target_squares.get(current_square, []) + [rook_square]

                    # If piece on target square and not friendly, go to next direction
                    if target_piece:
                        break


    def generate_cannon_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal cannon moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.cannon]:
            # Going through chosen direction indices
            for dir_idx in range(4):
                offset = self.dir_offsets[dir_idx]
                in_attack_mode = False
                target_piece = False
                # "Walking" in direction using direction offsets
                for step in range(self.dist_to_edge[current_square][dir_idx]):
                    target_square = current_square + offset * (step + 1)

                    if in_attack_mode:
                        target_piece = self.board.squares[target_square]
                        # if target square is empty, continue
                        if not target_piece:
                            continue

                        # If target_piece is friendly, go to next direction
                        if Piece.is_color(target_piece, self.friendly):
                            break

                    elif self.board.squares[target_square]:
                        in_attack_mode = True
                        continue
                    # If piece on target square and not friendly, add move and go to next direction
                    self.moves.add((current_square, target_square))
                    self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                    if target_piece:
                        break


    def flying_general(self):
        # red: down
        # black: up
        dir_idx = self.opponent * 2
        offset = self.dir_offsets[dir_idx]
        block = None
        for step in range(self.dist_to_edge[self.opponent_king][dir_idx]):
            square = self.opponent_king + offset * (step + 1)
            piece = self.board.squares[square]

            if not piece:
                continue
            # Opponent piece blocks any pins, but can't be captured 
            # by friendly king as opponent king's defending it
            if Piece.is_color(piece, self.opponent):
                if not block:
                    self.king_attack_map.add(square)
                return

            # Friendly king
            if Piece.is_type(piece, Piece.king):
                if block:
                    # Pin piece, double pin it if already pinned
                    self.double_pinned.add(block) if block in self.pinned_squares else self.pinned_squares.add(block)
                    print("PIN BY KING")
                else:
                    self.double_check = self.check
                    self.check = True 
                return

            # Second friendly piece in direction, no pins possible
            if block:
                return
            block = square
        
        # If there're no pieces between opponent king and opposite edge of board
        # friendly king can't move to the opponent king's file
        if block:
            return
        print("FLYING GENERAL THREAT")
        friendly_king_rank = self.friendly_king // 9
        opponent_king_file = self.opponent_king % 9
        flyin_general_square = friendly_king_rank * 9 + opponent_king_file
        self.king_attack_map.add(flyin_general_square)
        

    def calculate_horse_attack_data(self) -> None:
        opponent_horses = self.board.piece_lists[self.opponent][Piece.horse]
        for square in opponent_horses:
            for move in self.horse_moves[square]:
                target_square = move[1]
               
                # MISTAKE I MADE: 
                # Not adding squares to the attack map if they're occupied by an opponent piece allows 
                # the king to make pseudo-legal capture to squares that can be attacked by opponent pieces
                # Bugs like these are really valuable and virtually inevitable in complex applications 
                # if Piece.is_color(self.board.squares[target_square], self.opponent):
                #     continue

                block_square = self.board.get_horse_block(square, target_square)
                block_piece = self.board.squares[block_square]
                is_move_check = target_square == self.friendly_king

                # Horse is attacking the target square
                if not block_piece:
                    self.horse_attack_map.add(target_square)
                    if is_move_check:
                        self.double_check = self.check
                        self.check = True
                        print("HORSE CHECK")
                    continue

                # Move is blocked by opponent piece or wouldn't threaten friendly king anyways
                if Piece.is_color(block_piece, self.opponent) or not is_move_check:
                    continue

                # If blocked by friendly piece, it's pinned
                if block_square in self.pinned_squares:
                    # If already pinned, double pin it
                    self.double_pinned.add(target_square)
                    continue
                self.pinned_squares.add(target_square)

    
    def generate_cannon_attack_map(self):
        for square in self.board.piece_lists[self.opponent][Piece.cannon]:
            for dir_idx in range(4):
                offset = self.dir_offsets[dir_idx]
                block = False
                double_block = False
                for step in range(self.dist_to_edge[square][dir_idx]):
                    attacking_square = square + offset * (step + 1)
                    piece = self.board.squares[attacking_square]
                    
                    # Cannon is in capture mode
                    if block:
                        self.cannon_attack_map.add(attacking_square)

                    # attacking square is occupied
                    if piece:
                        double_block = block
                        block = True

                    if double_block:
                        break


    def calculate_cannon_attack_data(self) -> None:
        self.generate_cannon_attack_map()
        for dir_idx in range(4):
            offset = self.dir_offsets[dir_idx]
            friendly_blocks = set()
            block = False
            double_block = False
            for step in range(self.dist_to_edge[self.friendly_king][dir_idx]):
                attacking_square = self.friendly_king + offset * (step + 1)
                piece = self.board.squares[attacking_square]
                # Skip empty squares
                if not piece:
                    continue
                # Piece is opponent cannon
                if Piece.is_color(piece, self.opponent) and Piece.is_type(piece, Piece.cannon):
                    if double_block:
                        self.pinned_squares |= friendly_blocks
                    elif block:
                        self.double_check = self.check
                        self.check = True

                # This is the third piece we come across, 
                # thus preventing any checks / pins in current direction
                if double_block:
                    break
                # If piece is friendly, we add it to the friendly blocks
                if Piece.is_color(piece, self.friendly):
                    friendly_blocks.add(attacking_square)

                # First piece: block
                # Second piece: double block    
                double_block = block
                block = True


    def generate_rook_attack_map(self) -> None:
        for square in self.board.piece_lists[self.opponent][Piece.rook]:
            for dir_idx in range(4):
                offset = self.dir_offsets[dir_idx]
                for step in range(self.dist_to_edge[square][dir_idx]):
                    attacking_square = square + offset * (step + 1)
                    piece = self.board.squares[attacking_square]
                    
                    self.rook_attack_map.add(attacking_square)
                    # Attacking square occupied, break
                    if piece:
                        break


    def calculate_rook_attack_data(self) -> None:
        self.generate_rook_attack_map()
        for dir_idx in range(4):
            offset = self.dir_offsets[dir_idx]
            friendly_block = None
            for step in range(self.dist_to_edge[self.friendly_king][dir_idx]):
                attacking_square = self.friendly_king + offset * (step + 1)
                piece = self.board.squares[attacking_square]
                # Skip empty squares
                if not piece:
                    continue  
                # Friendly piece
                if Piece.is_color(piece, self.friendly):
                    # Second friendly piece along current direction, so no pins possible
                    if friendly_block:
                        break
                    friendly_block = attacking_square
                    continue
                
                # Opponent piece isn't a rook, avoiding any checks and pins
                if not Piece.is_type(piece, Piece.rook):
                    break

                # Opponent rook
                # There's one friendly piece along the current direction, so (double-) pin it 
                if friendly_block:
                    if attacking_square in self.pinned_squares:
                        self.double_pinned.add(attacking_square)
                        break
                    self.pinned_squares.add(attacking_square)
                    break
                # If there're no friendly blocks, it's a check
                self.double_check = self.check
                self.check = True
                break

    def generate_pawn_attack_map(self) -> None:
        for square in self.board.piece_lists[self.opponent][Piece.pawn]:
            for attacking_square in self.pawn_moves[self.opponent][square]:
                piece = self.board.squares[attacking_square]

                if Piece.is_color(piece, self.friendly):
                    if Piece.is_type(piece, Piece.king):
                        self.double_check = self.check
                        self.check = True
                    continue
                # Empty square or opponent piece
                self.pawn_attack_map.add(attacking_square)
                    

    def calculate_attack_data(self) -> None:
        self.flying_general()
        self.calculate_horse_attack_data()
        self.calculate_cannon_attack_data()
        self.calculate_rook_attack_data()
        self.generate_pawn_attack_map()
        print("DOUBLE CHECK: ", self.double_check)
        self.attack_map |= self.horse_attack_map | self.rook_attack_map | self.cannon_attack_map | self.pawn_attack_map | self.king_attack_map
        print(self.attack_map) 