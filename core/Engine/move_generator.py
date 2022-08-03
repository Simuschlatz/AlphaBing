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
        cls.horse_attack_map = set()
        cls.rook_attack_map = set()
        cls.cannon_attack_map = set()
        cls.pawn_attack_map = set()
        cls.king_attack_map = set()

        cls.illegal_squares = set()
        cls.pinned_squares = set()
        cls.checks = 0
        cls.block_check_hash = {}
        cls.checking_cannon_square = None
        cls.cause_cannon_defect = None

        cls.iterations = 0

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
                # If there's a check (or multiple)
                # Only proceed if num of checks the moves blocks is equivalent to total num of checks
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
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
                    
                    if blocks_all_checks or not cls.checks:
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
        return num_checks_blocked == cls.checks + confusion_value


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
                    cls.king_attack_map.add(square)
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
        # print("FLYING GENERAL THREAT")
        opponent_king_file = cls.opponent_king % 9
        flyin_general_square = friendly_king_rank * 9 + opponent_king_file
        cls.king_attack_map.add(flyin_general_square)
        
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
                    cls.horse_attack_map.add(target_square)
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
        for target_square in cls.king_move_map[cls.board.moving_side][cls.moving_king]:
            # Excluding squares occupied by friendly pieces
            piece_on_target = cls.board.squares[target_square]
            if Piece.is_color(piece_on_target, cls.board.moving_color):
                continue
            # Looping over opponent cannons
            for cannon in cls.board.piece_lists[cls.board.opponent_side][Piece.cannon]:
                dir_idx = cls.get_orth_dir_idx(cannon, target_square)
                # If cannon could threaten king's move, generate attack ray
                if dir_idx != None:
                    cls.generate_cannon_attack_ray(cannon, dir_idx)

            for rook in cls.board.piece_lists[cls.board.opponent_side][Piece.rook]:
                dir_idx = cls.get_orth_dir_idx(rook, target_square)
                # If cannon could threaten king's move, generate attack ray
                if dir_idx != None:
                    cls.generate_rook_attack_ray(rook, dir_idx)
                

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
                cls.cannon_attack_map.add(attacking_square)

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
    def get_cannon_imposed_limits(cls):
        """
        Adds pins and illegal squares to instance variables "pinned_squares" and "illegal_squares" 
        """
        target_squares = cls.orthogonal_move_map[cls.moving_king] # {square: [...], [...], ...}
        for targets_in_dir in target_squares.values():
            # A screen is the piece between opponent cannon and the captured piece
            friendly_screens = set()
            screens = set()
            double_block = False
            visited_squares = set()
            for attacking_square in targets_in_dir:
                piece = cls.board.squares[attacking_square]
                visited_squares.add(attacking_square)
                # Skip empty squares
                if not piece:
                    continue

                if Piece.is_color(piece, cls.board.opponent_color) and Piece.is_type(piece, Piece.cannon):
                    if double_block:
                        cls.pinned_squares |= friendly_screens
                        # cls.illegal_squares |= screens - friendly_screens
                        break
                    # Single screen
                    if screens:
                        cls.checks += 1
                        # Can't capture enemy screen, as it would still be check
                        cls.illegal_squares |= screens - friendly_screens
                        # Fiendly screen / block piece can prevent check by moving away
                        if friendly_screens:
                            cls.cause_cannon_defect = next(iter(friendly_screens))
                        cls.checking_cannon_square = attacking_square
                        # Can move to any visited square except the screen to prevent check
                        for block_square in visited_squares - screens:
                            cls.block_check_hash[block_square] = cls.block_check_hash.get(block_square, 0) + 1
                    else:
                        # All squares between king and opponent cannon empty, so mark them as illegal
                        # as moving to any of them would result in a check
                        cls.illegal_squares |= visited_squares - {attacking_square}

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
    def generate_rook_pins(cls):
        for dir_idx in range(4):
            offset = cls.dir_offsets[dir_idx]
            friendly_block = None
            visited_squares = set()
            for step in range(cls.dist_to_edge[cls.moving_king][dir_idx]):
                attacking_square = cls.moving_king + offset * (step + 1)
                piece = cls.board.squares[attacking_square]
                visited_squares.add(attacking_square)
                # Skip empty squares
                if not piece:
                    continue  
                # Friendly piece
                if Piece.is_color(piece, cls.board.moving_color):
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
    def calculate_pawn_attack_data(cls) -> None:
        for square in cls.board.piece_lists[cls.board.opponent_side][Piece.pawn]:
            for attacking_square in cls.pawn_move_map[cls.board.opponent_side][square]:
                piece = cls.board.squares[attacking_square]

                if Piece.is_color(piece, cls.board.moving_color):
                    if Piece.is_type(piece, Piece.king):
                        cls.checks += 1
                        cls.block_check_hash[square] = cls.block_check_hash.get(square, 0) + 1
                    continue
                # Empty square or opponent piece
                cls.pawn_attack_map.add(attacking_square)
                    
    @classmethod
    def calculate_attack_data(cls) -> None:
        cls.exclude_king_moves()
        cls.flying_general()
        cls.calculate_horse_attack_data()
        cls.get_cannon_imposed_limits()
        cls.generate_rook_pins()
        cls.calculate_pawn_attack_data()
        # print("CHECK: ", cls.checks)
        cls.attack_map |= cls.horse_attack_map | cls.rook_attack_map | cls.cannon_attack_map | cls.pawn_attack_map | cls.king_attack_map
        # print("SQUARES BLOCKING CHECK: ", cls.block_check_hash) 
