from piece import Piece
from precomputed_move_maps import Precomputing_moves

class Legal_move_generator:
    """
    Generates legal moves from pseudo-legal-move-maps \n
    call load_moves() to receive a list of all legal moves for the current state of the game.
    """
    Precomputing_moves.init_constants()
    dir_offsets = Precomputing_moves.dir_offsets
    dist_to_edge = Precomputing_moves.dist_to_edge

    # Precalculating move maps
    king_move_map = Precomputing_moves.precompute_king_moves()
    orthogonal_move_map = Precomputing_moves.precompute_rook_moves()
    horse_move_map = Precomputing_moves.precompute_horse_moves()
    advisor_move_map = Precomputing_moves.precompute_advisor_moves()
    elephant_move_map = Precomputing_moves.precompute_elephant_moves()
    pawn_move_map = Precomputing_moves.precompute_pawn_moves()

    @classmethod
    def load_moves(cls, board) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible moves
        """
        cls.board = board
        cls.init()
        cls.calculate_attack_data()
        cls.generate_king_moves()
        cls.generate_rook_moves()
        cls.generate_cannon_moves()
        cls.generate_horse_moves()
        cls.generate_advisor_moves()
        cls.generate_pawn_moves()
        cls.generate_elephant_moves()

        return cls.moves
    
    @classmethod
    def init(cls):
        # variable "moving" can be used for indexing and determining the color of piece 
        # (see "piece.py > class Piece") here e.g. allows to only loop over friendly indices
        cls.friendly = cls.board.moving_color
        cls.opponent = 1 - cls.friendly
        cls.friendly_king = list(cls.board.piece_lists[cls.friendly][Piece.king]).pop()
        cls.opponent_king = list(cls.board.piece_lists[cls.opponent][Piece.king]).pop()
        cls.flying_general_possibility = cls.friendly_king % 9 == cls.opponent_king % 9

        cls.moves = []
        cls.target_squares = {}

        cls.attack_map = set()
        cls.horse_attack_map = set()
        cls.rook_attack_map = set()
        cls.cannon_attack_map = set()
        cls.pawn_attack_map = set()
        cls.king_attack_map = set()

        cls.illegal_squares = set()
        cls.pinned_squares = set()
        cls.checks = 0
        cls.block_check_hash = {}
        cls.prevents_cannon_check = set()
    
    @classmethod
    def generate_king_moves(cls) -> None:
        current_square = cls.friendly_king

        target_squares = cls.king_move_map[cls.friendly][current_square]
        for target_square in target_squares:
            if target_square in cls.attack_map:
                continue
            target_piece = cls.board.squares[target_square]
            if Piece.is_color(target_piece, cls.friendly):
                continue
            cls.moves.append((current_square, target_square))
            cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]

    @classmethod
    def generate_pawn_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal pawn moves
        """
        # Looping over friendly pawns
        for current_square in cls.board.piece_lists[cls.friendly][Piece.pawn]:
            if cls.checks and cls.is_pinned(current_square):
                break
            avoids_cannon_check = current_square in cls.prevents_cannon_check
            target_squares = cls.pawn_move_map[cls.friendly][current_square]

            for target_square in target_squares:
                dir_idx = cls.dir_offsets.index(target_square - current_square)
                if cls.is_pinned(current_square) and not cls.moves_along_ray(cls.friendly_king, current_square, dir_idx):
                    continue
                if target_square in cls.illegal_squares:
                    continue
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.friendly):
                    continue

                cls.moves.append((current_square, target_square))
                cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]
                # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and cls.checks and not avoids_cannon_check:
                    break
    
    @classmethod
    def generate_elephant_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal elephant moves
        """
        for current_square in cls.board.piece_lists[cls.friendly][Piece.elephant]:
            if cls.is_pinned(current_square):
                continue
            illegal_squares = set()
            avoids_cannon_check = current_square in cls.prevents_cannon_check
            target_squares = cls.elephant_move_map[cls.friendly][current_square]
            
            for dir_idx in range(4, 8):
                # Checking for blocks
                if cls.dist_to_edge[current_square][dir_idx] < 1:
                    continue

                offset = cls.dir_offsets[dir_idx]
                blocking_square = current_square + offset

                if cls.board.squares[blocking_square]:
                    illegal_squares.add(current_square + offset * 2)

            # Removing illegal target squares
            target_squares = list(set(target_squares) - illegal_squares)
            
            for target_square in target_squares:
                if target_square in cls.illegal_squares:
                    continue

                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.friendly):
                    continue

                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                cls.moves.append((current_square, target_square))
                cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]
                # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and cls.checks and not avoids_cannon_check:
                    break

    @classmethod
    def generate_advisor_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal advisor moves
        """
        for current_square in cls.board.piece_lists[cls.friendly][Piece.advisor]:
            if cls.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square in cls.prevents_cannon_check
            target_squares = cls.advisor_move_map[cls.friendly][current_square]

            for target_square in target_squares:
                if target_square in cls.illegal_squares:
                    continue

                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue

                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.friendly):
                    continue
                cls.moves.append((current_square, target_square))
                cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]
                 # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and cls.checks and not avoids_cannon_check:
                    break

    @classmethod
    def generate_horse_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal horse moves
        """
        for current_square in cls.board.piece_lists[cls.friendly][Piece.horse]:
            if cls.is_pinned(current_square):
                continue
            horse_moves = cls.horse_move_map[current_square]

            # legal_moves = list(filter(lambda move: move in illegal_moves, legal_moves))
            for move in horse_moves:
                target_square = move[1]
                if target_square in cls.illegal_squares:
                    continue
                # If there's a check (or multiple)
                # Only proceed if num of checks the moves blocks is equivalent to total num of checks
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.friendly):
                    continue
                blocking_square = cls.board.get_horse_block(current_square, target_square)
                is_move_blocked = cls.board.squares[blocking_square]
                if is_move_blocked:
                    continue
                cls.moves.append((current_square, target_square))
                cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]

    @classmethod
    def generate_rook_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal rook moves
        """
        for current_square in cls.board.piece_lists[cls.friendly][Piece.rook]:
            if cls.checks and cls.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square in cls.prevents_cannon_check
            rook_attack_map = cls.orthogonal_move_map[current_square]
            # Going through chosen direction indices
            for dir_idx, squares_in_dir in rook_attack_map.items():
                if cls.is_pinned(current_square) and not cls.moves_along_ray(cls.friendly_king, current_square, dir_idx):
                    continue
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in squares_in_dir:
                    if target_square in cls.illegal_squares:
                        continue

                    target_piece = cls.board.squares[target_square]
                    blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                    if not blocks_all_checks:
                        if target_piece:
                            break
                        continue

                    # If target_piece is friendly, go to next direction
                    if Piece.is_color(target_piece, cls.friendly):
                        break
                    cls.moves.append((current_square, target_square))
                    cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]
                    # If piece on target square and not friendly, go to next direction
                    if target_piece:
                        break
                    # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                    if blocks_all_checks and cls.checks and not avoids_cannon_check:
                        break

    @classmethod
    def generate_cannon_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal cannon moves
        """
        for current_square in cls.board.piece_lists[cls.friendly][Piece.cannon]:
            if cls.checks and cls.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square in cls.prevents_cannon_check
            cannon_attack_map = cls.orthogonal_move_map[current_square]
            for dir_idx, targets_in_dir in cannon_attack_map.items():
                if cls.is_pinned(current_square) and not cls.moves_along_ray(cls.friendly_king, current_square, dir_idx):
                    continue
                in_attack_mode = False
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in targets_in_dir:

                    if cls.board.squares[target_square] and not in_attack_mode:
                        in_attack_mode = True
                        continue
                    # Can't move to or capture pieces on squares that would result in check
                    if target_square in cls.illegal_squares:
                        continue
                    
                    blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                    if not blocks_all_checks:
                        continue
                    
                    if in_attack_mode:
                        target_piece = cls.board.squares[target_square]
                        # if target square is empty, continue
                        if not target_piece:
                            continue

                        # If target_piece is friendly, go to next direction
                        if Piece.is_color(target_piece, cls.friendly):
                            break

                    cls.moves.append((current_square, target_square))
                    cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]
                    if target_piece:
                        break
                    if blocks_all_checks and cls.checks and not avoids_cannon_check:
                        break


    @classmethod
    def blocks_all_checks(cls, current_square, target_square):
        # If the piece is a screen for opponent cannon and moves out of the way,
        # it prevents the cannon check, thus counting as a blocked check
        disables_cannon = current_square in cls.prevents_cannon_check
        num_checks_blocked = cls.block_check_hash.get(target_square, 0) + disables_cannon
        return num_checks_blocked == cls.checks

    @classmethod
    def is_pinned(cls, square):
        return square in cls.pinned_squares
    
    @classmethod
    def moves_along_ray(cls, king_square: int, current_square: int, dir_idx: int):
        """
        :return: bool if move keeps a piece along the ray between two squares \n
        only to be used for orthogonally moving pieces.
        """
        target_square = current_square + cls.dir_offsets[dir_idx]
        pin_ray_delta_dist = abs(current_square - king_square) % 9
        move_ray_delta_dist = abs(target_square - king_square) % 9

        return pin_ray_delta_dist == move_ray_delta_dist

#-------------------------------------------------------------------------------
#-------The part below is for calculating pins, checks, double cheks etc.-------
#-------------------------------------------------------------------------------
    @classmethod
    def flying_general(cls):
        # red: down
        # black: up
        dir_idx = cls.opponent * 2
        offset = cls.dir_offsets[dir_idx]
        block = None
        for step in range(cls.dist_to_edge[cls.opponent_king][dir_idx]):
            square = cls.opponent_king + offset * (step + 1)
            piece = cls.board.squares[square]

            if not piece:
                continue
            # Opponent piece blocks any pins, but can't be captured 
            # by friendly king as opponent king's defending it
            if Piece.is_color(piece, cls.opponent):
                if not block:
                    cls.king_attack_map.add(square)
                return

            # Friendly king
            if Piece.is_type(piece, Piece.king):
                if block:
                    # Pin piece
                    cls.pinned_squares.add(block)
                else:
                    cls.checks += 1
                return

            # Second friendly piece in direction, no pins possible
            if block:
                return
            block = square
        
        # If there're no pieces between opponent king and opposite edge of board
        # friendly king can't move to the opponent king's file
        if block:
            return
        # print("FLYING GENERAL THREAT")
        friendly_king_rank = cls.friendly_king // 9
        opponent_king_file = cls.opponent_king % 9
        flyin_general_square = friendly_king_rank * 9 + opponent_king_file
        cls.king_attack_map.add(flyin_general_square)
        
    @classmethod
    def calculate_horse_attack_data(cls) -> None:
        opponent_horses = cls.board.piece_lists[cls.opponent][Piece.horse]
        for square in opponent_horses:
            for move in cls.horse_move_map[square]:
                target_square = move[1]
               
                # MISTAKE I MADE: 
                # Not adding squares to the attack map if they're occupied by an opponent piece allows 
                # the king to make pseudo-legal capture to squares that can be attacked by opponent pieces
                # Bugs like these are really valuable and virtually inevitable in complex applications 
                # if Piece.is_color(cls.board.squares[target_square], cls.opponent):
                #     continue

                block_square = cls.board.get_horse_block(square, target_square)
                block_piece = cls.board.squares[block_square]
                is_move_check = target_square == cls.friendly_king

                # Horse is attacking the target square
                if not block_piece:
                    cls.horse_attack_map.add(target_square)
                    if is_move_check:
                        cls.checks += 1
                        cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                    continue
                # Move is blocked by opponent piece or wouldn't threaten friendly king anyways
                if Piece.is_color(block_piece, cls.opponent) or not is_move_check:
                    continue
                # If blocked by friendly piece and move would result in check, it's pinned
                cls.pinned_squares.add(block_square)

    @classmethod
    def generate_cannon_attack_map(cls):
        for square in cls.board.piece_lists[cls.opponent][Piece.cannon]:
            for dir_idx in range(4):
                offset = cls.dir_offsets[dir_idx]
                block = False
                double_block = False
                for step in range(cls.dist_to_edge[square][dir_idx]):
                    attacking_square = square + offset * (step + 1)
                    piece = cls.board.squares[attacking_square]
                    # Cannon is in capture mode
                    if block:
                        cls.cannon_attack_map.add(attacking_square)
                    # attacking square is occupied
                    if piece:
                        double_block = block
                        block = True
                    if Piece.is_color(piece, cls.friendly) and Piece.is_type(piece, Piece.king):
                        continue
                    if double_block:
                        break

    @classmethod
    def get_cannon_imposed_limits(cls):
        """
        Adds pins and illegal squares to instance variables "pinned_squares" and "illegal_squares" 
        """
        for dir_idx in range(4):
            offset = cls.dir_offsets[dir_idx]
            # A screen is the piece between opponent cannon and the captured piece
            friendly_screens = set()
            screens = set()
            double_block = False
            visited_squares = set()

            for step in range(cls.dist_to_edge[cls.friendly_king][dir_idx]):
                attacking_square = cls.friendly_king + offset * (step + 1)
                piece = cls.board.squares[attacking_square]
                visited_squares.add(attacking_square)
                # Skip empty squares
                if not piece:
                    continue

                if Piece.is_color(piece, cls.opponent) and Piece.is_type(piece, Piece.cannon):
                    if double_block:
                        cls.illegal_squares |= screens - friendly_screens
                        cls.pinned_squares |= friendly_screens
                        break
                    if screens:
                        cls.checks += 1
                        # Can't capture enemy screens, as it would still be check
                        cls.illegal_squares |= screens - friendly_screens
                        # Fiendly screen / block piece can prevent check by moving away
                        cls.prevents_cannon_check |= friendly_screens
                        # Can move to any visited square except the screen to prevent check
                        for block_square in visited_squares - screens:
                            cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                    # All squares between king and opponent cannon empty, so mark them as illegal
                    # as moving to any of them would result in a check
                    else:
                        cls.illegal_squares |= visited_squares - {attacking_square}

                # This is the third piece we come across, 
                # thus preventing any checks / pins in current direction
                if double_block:
                    break
                # If piece is friendly, we add it to the friendly blocks
                if Piece.is_color(piece, cls.friendly):
                    friendly_screens.add(attacking_square)

                # First piece: block
                # Second piece: double block    
                double_block = bool(screens)
                screens.add(attacking_square)

    @classmethod
    def calculate_cannon_attack_data(cls) -> None:
        cls.generate_cannon_attack_map()
        cls.get_cannon_imposed_limits()

    @classmethod
    def generate_rook_attack_map(cls) -> None:
        for square in cls.board.piece_lists[cls.opponent][Piece.rook]:
            for dir_idx in range(4):
                offset = cls.dir_offsets[dir_idx]
                for step in range(cls.dist_to_edge[square][dir_idx]):
                    attacking_square = square + offset * (step + 1)
                    piece = cls.board.squares[attacking_square]
                    
                    cls.rook_attack_map.add(attacking_square)
                    # Attacking square occupied, break
                    if piece:
                        break

    @classmethod
    def generate_rook_pins(cls):
        for dir_idx in range(4):
            offset = cls.dir_offsets[dir_idx]
            friendly_block = None
            visited_squares = set()
            for step in range(cls.dist_to_edge[cls.friendly_king][dir_idx]):
                attacking_square = cls.friendly_king + offset * (step + 1)
                piece = cls.board.squares[attacking_square]
                visited_squares.add(attacking_square)
                # Skip empty squares
                if not piece:
                    continue  
                # Friendly piece
                if Piece.is_color(piece, cls.friendly):
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
                    cls.pinned_squares.add(friendly_block)
                    break
                # If there're no blocks, it's a check
                cls.checks += 1
                # Can move to any visited square except the block to prevent check
                # Here, removing the friendly block isn't really necessary as friendly pieces can't be captured anyways,
                # but hash map lookups are probably faster than checking for a piece's color later in the process
                for block_square in visited_squares - {friendly_block}:
                    cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                break  

    @classmethod
    def calculate_rook_attack_data(cls) -> None:
        cls.generate_rook_attack_map()
        cls.generate_rook_pins()

    @classmethod
    def calculate_pawn_attack_data(cls) -> None:
        for square in cls.board.piece_lists[cls.opponent][Piece.pawn]:
            for attacking_square in cls.pawn_move_map[cls.opponent][square]:
                piece = cls.board.squares[attacking_square]

                if Piece.is_color(piece, cls.friendly):
                    if Piece.is_type(piece, Piece.king):
                        cls.checks += 1
                    continue
                # Empty square or opponent piece
                cls.pawn_attack_map.add(attacking_square)
                    
    @classmethod
    def calculate_attack_data(cls) -> None:
        cls.flying_general()
        cls.calculate_horse_attack_data()
        cls.calculate_cannon_attack_data()
        cls.calculate_rook_attack_data()
        cls.calculate_pawn_attack_data()
        # print("CHECK: ", cls.checks)
        cls.attack_map |= cls.horse_attack_map | cls.rook_attack_map | cls.cannon_attack_map | cls.pawn_attack_map | cls.king_attack_map
        # print("SQUARES BLOCKING CHECK: ", cls.block_check_hash) 