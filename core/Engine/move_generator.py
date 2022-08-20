from Engine.piece import Piece
from Engine.precomputed_move_maps import Precomputing_moves

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
    orthogonal_move_map = Precomputing_moves.precompute_orthogonal_moves()
    horse_move_map = Precomputing_moves.precompute_horse_moves()
    advisor_move_map = Precomputing_moves.precompute_advisor_moves()
    elephant_move_map = Precomputing_moves.precompute_elephant_moves()
    pawn_move_map = Precomputing_moves.precompute_pawn_moves()

    @classmethod
    def init_board(cls, board):
        cls.board = board

    @classmethod
    def load_moves(cls) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible moves
        """
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
        """
        Initializes data used for move generation
        """
        cls.moving_king = next(iter(cls.board.piece_lists[cls.board.moving_side][Piece.king]))
        cls.opponent_king = next(iter(cls.board.piece_lists[cls.board.opponent_side][Piece.king]))

        cls.moves = []
        cls.target_squares = {}

        cls.attack_map = set()

        # Opponent king can only pose a threat if it's file's dist to friendly king's file is exactly 1
        cls.friendly_king_file = cls.moving_king % 9
        cls.opponent_king_file = cls.opponent_king % 9
        cls.flying_general_threat = abs(cls.friendly_king_file - cls.opponent_king_file) == 1
        
        # Squares that would serve as screen for a threatening cannon
        cls.illegal_squares = set()
        cls.pinned_squares = set()
        # Number of checks
        cls.checks = 0
        # Used for tracking the number of checks a square would block if moved to
        cls.block_check_hash = {}
        # Square used to denote a checking cannon if existing
        cls.checking_cannon_square = None
        # squares occupied by friendly pieces that are part of two pieces blocking a cannon check that can't
        # capture the other piece of double block as it would rearrange the double block into single screen
        cls.double_screens = set()
        # Sqaure of friendly piece that serves as screen for a checking cannon, 
        # whose movement away from check-ray would resolve th check
        cls.cause_cannon_defect = None

    @classmethod
    def generate_king_moves(cls) -> None:
        current_square = cls.moving_king

        target_squares = cls.king_move_map[cls.board.moving_side][current_square]
        for target_square in target_squares:
            if target_square in cls.attack_map:
                continue
            target_piece = cls.board.squares[target_square]
            if Piece.is_color(target_piece, cls.board.moving_color):
                continue
            cls.moves.append((current_square, target_square))
            cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]


    @classmethod
    def generate_pawn_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal pawn moves
        """
        # Looping over friendly pawns
        for current_square in cls.board.piece_lists[cls.board.moving_side][Piece.pawn]:
            is_pinned = cls.is_pinned(current_square)
            if cls.checks and is_pinned:
                break
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            target_squares = cls.pawn_move_map[cls.board.moving_side][current_square]

            for target_square in target_squares:
                dir_idx = cls.dir_offsets.index(target_square - current_square)
                if is_pinned and not cls.moves_along_ray(cls.moving_king, current_square, dir_idx):
                    continue
                if target_square in cls.illegal_squares:
                    continue
                captures_checking_cannon = cls.checking_cannon_square == target_square
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square, captures_checking_cannon)
                if not blocks_all_checks:
                    continue
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
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
        for current_square in cls.board.piece_lists[cls.board.moving_side][Piece.elephant]:
            if cls.is_pinned(current_square):
                continue
            illegal_squares = set()
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            target_squares = cls.elephant_move_map[cls.board.moving_side][current_square]
            
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
                if Piece.is_color(target_piece, cls.board.moving_color):
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
        for current_square in cls.board.piece_lists[cls.board.moving_side][Piece.advisor]:
            if cls.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            target_squares = cls.advisor_move_map[cls.board.moving_side][current_square]

            for target_square in target_squares:
                if target_square in cls.illegal_squares:
                    continue

                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue

                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
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
        for current_square in cls.board.piece_lists[cls.board.moving_side][Piece.horse]:
            if cls.is_pinned(current_square):
                continue
            horse_moves = cls.horse_move_map[current_square]

            # legal_moves = list(filter(lambda move: move in illegal_moves, legal_moves))
            for move in horse_moves:
                target_square = move[1]
                if target_square in cls.illegal_squares:
                    continue
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
                    continue
                # If there's a check (or multiple)
                # Only proceed if num of checks the moves blocks is equivalent to total num of checks
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
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
        for current_square in cls.board.piece_lists[cls.board.moving_side][Piece.rook]:
            is_pinned = cls.is_pinned(current_square)
            if cls.checks and is_pinned:
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect

            rook_move_map = cls.orthogonal_move_map[current_square]
            # Going through chosen direction indices
            for dir_idx, squares_in_dir in rook_move_map.items():
                if is_pinned and not cls.moves_along_ray(cls.moving_king, current_square, dir_idx):
                    continue
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in squares_in_dir:
                    if target_square in cls.illegal_squares:
                        continue
                    target_piece = cls.board.squares[target_square]

                    # If target_piece is friendly, go to next direction
                    if Piece.is_color(target_piece, cls.board.moving_color):
                        break
                    
                    # Because all squares between the rook and cannon (inclusive) are in block_check_hash and
                    # current square is cause_cannon_defect, the number of checks blocked would be 2, not 1
                    # so it skips moves between cannon and rook, but would also skip the capture of checking cannon
                    # Thus, if rook is screen for checking cannon and captures it, increment the number of checks by 1
                    # => condition 2 == 1 becomes 2 == 2
                    captures_checking_cannon = avoids_cannon_check and cls.checking_cannon_square == target_square
                    blocks_all_checks = cls.blocks_all_checks(current_square, target_square, captures_checking_cannon)
                    
                    if not blocks_all_checks:
                        continue
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
        for current_square in cls.board.piece_lists[cls.board.moving_side][Piece.cannon]:
            is_pinned = cls.is_pinned(current_square)
            if cls.checks and is_pinned:
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            cannon_attack_map = cls.orthogonal_move_map[current_square]

            for dir_idx, targets_in_dir in cannon_attack_map.items():
                if is_pinned and not cls.moves_along_ray(cls.moving_king, current_square, dir_idx):
                    continue

                in_attack_mode = False
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in targets_in_dir:

                    if cls.board.squares[target_square] and not in_attack_mode:
                        in_attack_mode = True
                        continue

                    if in_attack_mode:
                        target_piece = cls.board.squares[target_square]
                        # if target square is empty, continue
                        if not target_piece:
                            continue
                        
                        # If target_piece is friendly, go to next direction
                        if Piece.is_color(target_piece, cls.board.moving_color):
                            break
                    # Can't move to or capture pieces on squares that would result in check
                    if target_square in cls.illegal_squares:
                        continue
                    
                    blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                    if not blocks_all_checks:
                        continue
                    
                    cls.moves.append((current_square, target_square))
                    cls.target_squares[current_square] = cls.target_squares.get(current_square, []) + [target_square]
                    # Move was a capture, can't move further in this direction 
                    if target_piece:
                        break
                    if blocks_all_checks and cls.checks and not avoids_cannon_check:
                        break


    @classmethod
    def blocks_all_checks(cls, current_square, target_square, confusion_value=0):
        # If the piece is a screen for opponent cannon and moves out of the way,
        # it prevents the cannon check, thus counting as a blocked check
        disables_cannon = current_square == cls.cause_cannon_defect
        num_checks_blocked = cls.block_check_hash.get(target_square, 0) + disables_cannon
        captures_other_double_screen = current_square in cls.double_screens and target_square in cls.double_screens
        return num_checks_blocked == cls.checks + confusion_value and not captures_other_double_screen


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


    @classmethod
    def get_orth_dir_idx(cls, square_1, square_2):
        """
        :return: direction index 0 to 4 between two squares from square_1's perspective
        """
        file_1, rank_1 = cls.board.get_file_and_rank(square_1)
        file_2, rank_2 = cls.board.get_file_and_rank(square_2)
        d_file = file_2 - file_1
        d_rank = rank_2 - rank_1
        # On same file
        if not d_file and d_rank:
            d_rank_norm = d_rank // abs(d_rank)
            return cls.dir_offsets.index(d_rank_norm * 9)
        # On same rank
        if not d_rank and d_file:
            d_file_norm = d_file // abs(d_file)
            return cls.dir_offsets.index(d_file_norm)
        return None


#-------------------------------------------------------------------------------
#-------The part below is for calculating pins, checks, double cheks etc.-------
#-------------------------------------------------------------------------------

    @classmethod
    def flying_general(cls):
        if not cls.flying_general_threat:
            return
        dir_idx = cls.board.moving_side * 2
        friendly_king_rank = cls.moving_king // 9 
        dist_kings = abs(friendly_king_rank - cls.opponent_king // 9)
        offset = cls.dir_offsets[dir_idx]
        block = None
        for step in range(dist_kings):
            square = cls.opponent_king + offset * (step + 1)
            piece = cls.board.squares[square]

            if not piece:
                continue
            # Opponent piece blocks any pins, but can't be captured 
            # by friendly king as opponent king's defending it
            if Piece.is_color(piece, cls.board.opponent_color):
                if not block:
                    cls.attack_map.add(square)
                return

            # Friendly king
            if Piece.is_type(piece ,Piece.king):
                # Pin piece
                cls.pinned_squares.add(block)
                return

            # Second friendly piece in direction, no pins possible
            if block:
                return
            block = square    
        # If there're no pieces between opponent king and opposite edge of board
        # friendly king can't move to the opponent king's file
        if block:
            return
        flying_general_square = friendly_king_rank * 9 + cls.opponent_king_file
        cls.attack_map.add(flying_general_square)
        
    @classmethod
    def calculate_horse_attack_data(cls) -> None:
        opponent_horses = cls.board.piece_lists[cls.board.opponent_side][Piece.horse]
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
                is_move_check = target_square == cls.moving_king

                # Horse is attacking the target square
                if not block_piece:
                    cls.attack_map.add(target_square)
                    if is_move_check:
                        cls.checks += 1
                        cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                    continue
                # Move is blocked by opponent piece or wouldn't threaten friendly king anyways
                if Piece.is_color(block_piece, cls.board.opponent_color) or not is_move_check:
                    continue
                # If blocked by friendly piece and move would result in check, it's pinned
                cls.pinned_squares.add(block_square)

    @classmethod
    def exclude_king_moves(cls):
        # Looping over possible king moves
        for move_dir_idx, target_square in enumerate(cls.king_move_map[cls.board.moving_side][cls.moving_king]):
            # Excluding squares occupied by friendly pieces
            piece_on_target = cls.board.squares[target_square]
            if Piece.is_color(piece_on_target, cls.board.moving_color):
                continue
            # Looping over opponent cannons
            for cannon in cls.board.piece_lists[cls.board.opponent_side][Piece.cannon]:
                attack_dir_idx = cls.get_orth_dir_idx(cannon, target_square)
                # If cannon could threaten king's move, generate attack ray
                if attack_dir_idx != None:
                    cls.generate_cannon_attack_ray(cannon, attack_dir_idx)

            for rook in cls.board.piece_lists[cls.board.opponent_side][Piece.rook]:
                attack_dir_idx = cls.get_orth_dir_idx(rook, target_square)
                # If cannon could threaten king's move, generate attack ray
                if attack_dir_idx != None:
                    cls.generate_rook_attack_ray(rook, attack_dir_idx)

            # Pawns can't capture backwards, so skip dir index relative to moving side
            if move_dir_idx == cls.board.moving_side * 2:
                continue

            for pawn in cls.board.piece_lists[cls.board.opponent_side][Piece.pawn]:
                mhd = cls.board.get_manhattan_dist(pawn, target_square)
                # Pawn is posing a threat to friendly king
                if not mhd:
                    cls.checks += 1
                    cls.block_check_hash[pawn] = cls.block_check_hash.get(pawn, 0) + 1
                # Pawn is able to attack a pseudo-legal target square of the king, making it illegal
                if mhd == 1:
                    cls.attack_map.add(target_square)

    @classmethod
    def confine_movement(cls) -> None:
        for cannon in cls.board.piece_lists[cls.board.opponent_side][Piece.cannon]:
            attack_dir_idx = cls.get_orth_dir_idx(cannon, cls.moving_king)
            # If cannon could threaten king's move, generate attack ray
            if attack_dir_idx != None:
                cls.get_cannon_imposed_limits(cannon, attack_dir_idx)
        for rook in cls.board.piece_lists[cls.board.opponent_side][Piece.rook]:
            attack_dir_idx = cls.get_orth_dir_idx(rook, cls.moving_king)
            # If cannon could threaten king's move, generate attack ray
            if attack_dir_idx != None:
                cls.get_rook_imposed_limits(rook, attack_dir_idx)     


    @classmethod
    def generate_cannon_attack_ray(cls, square, dir_idx):
        """
        generates attack map along ray of given direction from given square
        """
        attack_ray = cls.orthogonal_move_map[square][dir_idx]
        screen = False
        double_block = False
        for attacking_square in attack_ray:
            piece = cls.board.squares[attacking_square]
            # attacking square is occupied
            # Cannon is in capture mode
            if screen:
                cls.attack_map.add(attacking_square)

            if Piece.is_color(piece, cls.board.moving_color) and Piece.is_type(piece, Piece.king):
                if screen: 
                    continue
                return

            if piece:
                double_block = screen
                screen = True            
            if double_block:
                return

    @classmethod
    def generate_rook_attack_ray(cls, square, dir_idx) -> None:
        attack_ray = cls.orthogonal_move_map[square][dir_idx]
        for attacking_square in attack_ray:
            piece = cls.board.squares[attacking_square]
            if Piece.is_color(piece, cls.board.moving_color) and Piece.is_type(piece, Piece.king):
                continue
            cls.attack_map.add(attacking_square)
            # Attacking square occupied, break
            if piece:
                break

    @classmethod
    def get_cannon_imposed_limits(cls, cannon, dir_idx):
        """
        Adds pins and illegal squares to instance variables "pinned_squares" and "illegal_squares" 
        """
        offset = cls.dir_offsets[dir_idx]
        # A screen is the piece between opponent cannon and the captured piece
        friendly_screens = set()
        screens = set()
        double_block = False
        visited_squares = {cannon}
        for step in range(cls.dist_to_edge[cannon][dir_idx]):
            attacking_square = cannon + offset * (step + 1)
            piece = cls.board.squares[attacking_square]
            visited_squares.add(attacking_square)
            # Skip empty squares
            if not piece:
                continue

            if attacking_square == cls.moving_king:
                opponent_screens = screens - friendly_screens
                # Double screen, blocking checks but pinning friendly screens
                if double_block:
                    # Friendly screens can't move away from current ray
                    cls.pinned_squares |= friendly_screens
                    # This is no viable solution to double screen capturing, because we
                    # only want to limit the friendly screen from capturing opponent screen
                    # if not friendly_screens:
                    #     continue
                    # for screen in opponent_screens:
                    #     cls.block_check_hash[screen] = cls.block_check_hash.get(screen, 0) - 1
                    print(screens)
                    cls.double_screens |= screens
                    # King can't capture any opponent screens as it would move him into check
                    cls.attack_map |= opponent_screens
                    break
                # Single screen
                if screens:
                    cls.checks += 1
                    # Can't capture enemy screen, as it would still be check
                    cls.illegal_squares |= opponent_screens
                    # Fiendly screen / block piece can prevent check by moving away
                    if friendly_screens:
                        cls.cause_cannon_defect = next(iter(friendly_screens))
                    cls.checking_cannon_square = cannon
                    # Can move to any visited square except the screen to prevent check
                    for block_square in visited_squares - screens:
                        cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                else:
                    # All squares between king and opponent cannon empty, so mark them as illegal
                    # as moving to any of them would result in a check
                    cls.illegal_squares |= visited_squares - {cannon}

            # This is the third piece we come across, thus preventing any checks / pins
            if double_block:
                break
            # If piece is friendly, we add it to the friendly blocks
            if Piece.is_color(piece, cls.board.moving_color):
                friendly_screens.add(attacking_square)

            # First piece: block - second piece: double block    
            double_block = bool(screens)
            screens.add(attacking_square)

    @classmethod
    def get_rook_imposed_limits(cls, rook, dir_idx):
        offset = cls.dir_offsets[dir_idx]
        friendly_block = None
        visited_squares = {rook}
        for step in range(cls.dist_to_edge[rook][dir_idx]):
            attacking_square = rook + offset * (step + 1)
            piece = cls.board.squares[attacking_square]
            visited_squares.add(attacking_square)
            # Skip empty squares
            if not piece:
                continue
            # Detects king
            if attacking_square == cls.moving_king:
                # There's one friendly piece along current direction, pin it 
                if friendly_block:
                    cls.pinned_squares.add(friendly_block)
                    return
                # If there're no blocks, it's a check
                cls.checks += 1
                # Can move to any visited square except the block to prevent check
                for block_square in visited_squares - {friendly_block}:
                    cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                return  

            # Friendly piece
            if Piece.is_color(piece, cls.board.moving_color):
                # Second friendly piece along current direction, so no pins possible
                if friendly_block:
                    return
                friendly_block = attacking_square
                continue
            # Opponent piece, avoiding any checks and pins
            return

    @classmethod
    def calculate_attack_data(cls) -> None:
        cls.exclude_king_moves()
        cls.flying_general()
        cls.calculate_horse_attack_data()
        cls.confine_movement()
        # print("CHECK: ", cls.checks)
        # print("SQUARES BLOCKING CHECK: ", cls.block_check_hash) 
