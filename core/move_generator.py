from piece import Piece
from precomputed_move_maps import Precomputing_moves

class Legal_move_generator:
    """
    Generates legal moves from pseudo-legal-move-maps \n
    call load_moves() to receive a list of all legal moves for the current state of the game.
    """
    def __init__(self, board) -> None:
        Precomputing_moves.init_constants()
        self.dir_offsets = Precomputing_moves.dir_offsets
        self.dist_to_edge = Precomputing_moves.dist_to_edge

        # Precalculating move maps
        self.king_move_map = Precomputing_moves.precompute_king_moves()
        self.orthogonal_move_map = Precomputing_moves.precompute_rook_moves()
        self.horse_move_map = Precomputing_moves.precompute_horse_moves()
        self.advisor_move_map = Precomputing_moves.precompute_advisor_moves()
        self.elephant_move_map = Precomputing_moves.precompute_elephant_moves()
        self.pawn_move_map = Precomputing_moves.precompute_pawn_moves()

        self.board = board


    def load_moves(self) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible moves
        color_to_move : int
        """
        self.init()
        self.calculate_attack_data()
        self.generate_king_moves()
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

        self.moves = []
        self.target_squares = {}

        self.attack_map = set()
        self.horse_attack_map = set()
        self.rook_attack_map = set()
        self.cannon_attack_map = set()
        self.pawn_attack_map = set()
        self.king_attack_map = set()

        self.illegal_squares = set()
        self.pinned_squares = set()
        self.checks = 0
        self.block_check_hash = {}
        self.prevents_cannon_check = set()
    

    def generate_king_moves(self) -> None:
        current_square = self.friendly_king

        target_squares = self.king_move_map[self.friendly][current_square]
        for target_square in target_squares:
            if target_square in self.attack_map:
                continue
            target_piece = self.board.squares[target_square]
            if Piece.is_color(target_piece, self.friendly):
                continue
            self.moves.append((current_square, target_square))
            self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]


    def generate_pawn_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal pawn moves
        """
        # Looping over friendly pawns
        for current_square in self.board.piece_lists[self.friendly][Piece.pawn]:
            if self.checks and self.is_pinned(current_square):
                break
            avoids_cannon_check = current_square in self.prevents_cannon_check
            target_squares = self.pawn_move_map[self.friendly][current_square]

            for target_square in target_squares:
                dir_idx = self.dir_offsets.index(target_square - current_square)
                if self.is_pinned(current_square) and not self.moves_along_ray(self.friendly_king, current_square, dir_idx):
                    continue
                if target_square in self.illegal_squares:
                    continue
                blocks_all_checks = self.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue

                self.moves.append((current_square, target_square))
                self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and self.checks and not avoids_cannon_check:
                    break

    def generate_elephant_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal elephant moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.elephant]:
            if self.is_pinned(current_square):
                continue
            illegal_squares = set()
            avoids_cannon_check = current_square in self.prevents_cannon_check
            target_squares = self.elephant_move_map[self.friendly][current_square]
            
            for dir_idx in range(4, 8):
                # Checking for blocks
                if self.dist_to_edge[current_square][dir_idx] < 1:
                    continue

                offset = self.dir_offsets[dir_idx]
                blocking_square = current_square + offset

                if self.board.squares[blocking_square]:
                    illegal_squares.add(current_square + offset * 2)

            # Removing illegal target squares
            target_squares = list(set(target_squares) - illegal_squares)
            
            for target_square in target_squares:
                if target_square in self.illegal_squares:
                    continue

                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue

                blocks_all_checks = self.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                self.moves.append((current_square, target_square))
                self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and self.checks and not avoids_cannon_check:
                    break


    def generate_advisor_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal advisor moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.advisor]:
            if self.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square in self.prevents_cannon_check
            target_squares = self.advisor_move_map[self.friendly][current_square]

            for target_square in target_squares:
                if target_square in self.illegal_squares:
                    continue

                blocks_all_checks = self.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue

                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue
                self.moves.append((current_square, target_square))
                self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                 # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and self.checks and not avoids_cannon_check:
                    break


    def generate_horse_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal horse moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.horse]:
            if self.is_pinned(current_square):
                continue
            horse_moves = self.horse_move_map[current_square]

            # legal_moves = list(filter(lambda move: move in illegal_moves, legal_moves))
            for move in horse_moves:
                target_square = move[1]
                if target_square in self.illegal_squares:
                    continue
                # If there's a check (or multiple)
                # Only proceed if num of checks the moves blocks is equivalent to total num of checks
                blocks_all_checks = self.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                target_piece = self.board.squares[target_square]
                if Piece.is_color(target_piece, self.friendly):
                    continue
                blocking_square = self.board.get_horse_block(current_square, target_square)
                is_move_blocked = self.board.squares[blocking_square]
                if is_move_blocked:
                    continue
                self.moves.append((current_square, target_square))
                self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]


    def generate_rook_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal rook moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.rook]:
            if self.checks and self.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square in self.prevents_cannon_check
            rook_attack_map = self.orthogonal_move_map[current_square]
            # Going through chosen direction indices
            for dir_idx, squares_in_dir in rook_attack_map.items():
                if self.is_pinned(current_square) and not self.moves_along_ray(self.friendly_king, current_square, dir_idx):
                    continue
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in squares_in_dir:
                    if target_square in self.illegal_squares:
                        continue

                    target_piece = self.board.squares[target_square]
                    blocks_all_checks = self.blocks_all_checks(current_square, target_square)
                    if not blocks_all_checks:
                        if target_piece:
                            break
                        continue

                    # If target_piece is friendly, go to next direction
                    if Piece.is_color(target_piece, self.friendly):
                        break
                    self.moves.append((current_square, target_square))
                    self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                    # If piece on target square and not friendly, go to next direction
                    if target_piece:
                        break
                    # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                    if blocks_all_checks and self.checks and not avoids_cannon_check:
                        break


    def generate_cannon_moves(self) -> None:
        """
        extends Legal_move_generator.moves with legal cannon moves
        """
        for current_square in self.board.piece_lists[self.friendly][Piece.cannon]:
            if self.checks and self.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square in self.prevents_cannon_check
            cannon_attack_map = self.orthogonal_move_map[current_square]
            for dir_idx, targets_in_dir in cannon_attack_map.items():
                if self.is_pinned(current_square) and not self.moves_along_ray(self.friendly_king, current_square, dir_idx):
                    continue
                in_attack_mode = False
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in targets_in_dir:

                    if self.board.squares[target_square] and not in_attack_mode:
                        in_attack_mode = True
                        continue
                    # Can't move to or capture pieces on squares that would result in check
                    if target_square in self.illegal_squares:
                        continue
                    
                    blocks_all_checks = self.blocks_all_checks(current_square, target_square)
                    if not blocks_all_checks:
                        continue
                    
                    if in_attack_mode:
                        target_piece = self.board.squares[target_square]
                        # if target square is empty, continue
                        if not target_piece:
                            continue

                        # If target_piece is friendly, go to next direction
                        if Piece.is_color(target_piece, self.friendly):
                            break

                    self.moves.append((current_square, target_square))
                    self.target_squares[current_square] = self.target_squares.get(current_square, []) + [target_square]
                    if target_piece:
                        break
                    if blocks_all_checks and self.checks and not avoids_cannon_check:
                        break



    def blocks_all_checks(self, current_square, target_square):
        # If the piece is a screen for opponent cannon and moves out of the way,
        # it prevents the cannon check, thus counting as a blocked check
        disables_cannon = current_square in self.prevents_cannon_check
        num_checks_blocked = self.block_check_hash.get(target_square, 0) + disables_cannon
        return num_checks_blocked == self.checks


    def is_pinned(self, square):
        return square in self.pinned_squares
    

    def moves_along_ray(self, king_square: int, current_square: int, dir_idx: int):
        """
        :return: bool if move keeps a piece along the ray between two squares \n
        only to be used for orthogonally moving pieces.
        """
        target_square = current_square + self.dir_offsets[dir_idx]
        pin_ray_delta_dist = abs(current_square - king_square) % 9
        move_ray_delta_dist = abs(target_square - king_square) % 9

        return pin_ray_delta_dist == move_ray_delta_dist

#-------------------------------------------------------------------------------
#-------The part below is for calculating pins, checks, double cheks etc.-------
#-------------------------------------------------------------------------------

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
                    # Pin piece
                    self.pinned_squares.add(block)
                    print("PIN BY KING")
                else:
                    self.checks += 1
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
            for move in self.horse_move_map[square]:
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
                        self.checks += 1
                        self.block_check_hash[block_square] = self.block_check_hash.get(block_square, 0) + 1
                    continue
                # Move is blocked by opponent piece or wouldn't threaten friendly king anyways
                if Piece.is_color(block_piece, self.opponent) or not is_move_check:
                    continue
                # If blocked by friendly piece and move would result in check, it's pinned
                self.pinned_squares.add(block_square)

    
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


    def get_cannon_imposed_limits(self):
        """
        Adds pins and illegal squares to instance variables "pinned_squares" and "illegal_squares" 
        """
        for dir_idx in range(4):
            offset = self.dir_offsets[dir_idx]
            # A screen is the piece between opponent cannon and the captured piece
            friendly_screens = set()
            screens = set()
            double_block = False
            visited_squares = set()

            for step in range(self.dist_to_edge[self.friendly_king][dir_idx]):
                attacking_square = self.friendly_king + offset * (step + 1)
                piece = self.board.squares[attacking_square]
                visited_squares.add(attacking_square)
                # Skip empty squares
                if not piece:
                    continue

                if Piece.is_color(piece, self.opponent) and Piece.is_type(piece, Piece.cannon):
                    if double_block:
                        self.illegal_squares |= screens - friendly_screens
                        self.pinned_squares |= friendly_screens
                        break
                    if screens:
                        self.checks += 1
                        # Can't capture enemy screens, as it would still be check
                        self.illegal_squares |= screens - friendly_screens
                        # Fiendly screen / block piece can prevent check by moving away
                        self.prevents_cannon_check |= friendly_screens
                        # Can move to any visited square except the screen to prevent check
                        for block_square in visited_squares - screens:
                            self.block_check_hash[block_square] = self.block_check_hash.get(block_square, 0) + 1
                    # All squares between king and opponent cannon empty, so mark them as illegal
                    # as moving to any of them would result in a check
                    else:
                        self.illegal_squares |= visited_squares - {attacking_square}

                # This is the third piece we come across, 
                # thus preventing any checks / pins in current direction
                if double_block:
                    break
                # If piece is friendly, we add it to the friendly blocks
                if Piece.is_color(piece, self.friendly):
                    friendly_screens.add(attacking_square)

                # First piece: block
                # Second piece: double block    
                double_block = bool(screens)
                screens.add(attacking_square)

    def calculate_cannon_attack_data(self) -> None:
        self.generate_cannon_attack_map()
        self.get_cannon_imposed_limits()


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


    def generate_rook_pins(self):
        for dir_idx in range(4):
            offset = self.dir_offsets[dir_idx]
            friendly_block = None
            visited_squares = set()
            for step in range(self.dist_to_edge[self.friendly_king][dir_idx]):
                attacking_square = self.friendly_king + offset * (step + 1)
                piece = self.board.squares[attacking_square]
                visited_squares.add(attacking_square)
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
                # There's one friendly piece along the current direction, so pin it 
                if friendly_block:
                    self.pinned_squares.add(friendly_block)
                    break
                # If there're no blocks, it's a check
                self.checks += 1
                # Can move to any visited square except the block to prevent check
                # Here, removing the friendly block isn't really necessary as friendly pieces can't be captured anyways,
                # but hash map lookups are probably faster than checking for a piece's color later in the process
                for block_square in visited_squares - {friendly_block}:
                    self.block_check_hash[block_square] = self.block_check_hash.get(block_square, 0) + 1
                break  


    def calculate_rook_attack_data(self) -> None:
        self.generate_rook_attack_map()
        self.generate_rook_pins()


    def calculate_pawn_attack_data(self) -> None:
        for square in self.board.piece_lists[self.opponent][Piece.pawn]:
            for attacking_square in self.pawn_move_map[self.opponent][square]:
                piece = self.board.squares[attacking_square]

                if Piece.is_color(piece, self.friendly):
                    if Piece.is_type(piece, Piece.king):
                        self.checks += 1
                    continue
                # Empty square or opponent piece
                self.pawn_attack_map.add(attacking_square)
                    

    def calculate_attack_data(self) -> None:
        self.flying_general()
        self.calculate_horse_attack_data()
        self.calculate_cannon_attack_data()
        self.calculate_rook_attack_data()
        self.calculate_pawn_attack_data()
        print("CHECK: ", self.checks)
        self.attack_map |= self.horse_attack_map | self.rook_attack_map | self.cannon_attack_map | self.pawn_attack_map | self.king_attack_map
        print("SQUARES BLOCKING CHECK: ", self.block_check_hash) 