"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
from core.Engine.piece import Piece
from core.Engine.precomputed_move_maps import PrecomputingMoves

# The code doesn't look well designed as there seem to be lots of repetitions, but reusing the same code is difficult, 
# as the order of operations for maximum performance vary from every piece's behavior
class LegalMoveGenerator:
    """
    Generates legal moves from pseudo-legal-move-maps \n
    call load_moves() to receive a list of all legal moves for the current state of the game.
    """
    PrecomputingMoves.init_constants()
    dir_offsets = PrecomputingMoves.dir_offsets
    dist_to_edge = PrecomputingMoves.dist_to_edge

    # Precalculating move maps
    king_mm = PrecomputingMoves.precompute_king_moves()
    orthogonal_mm = PrecomputingMoves.precompute_orthogonal_moves()
    horse_mm = PrecomputingMoves.precompute_horse_moves()
    advisor_mm = PrecomputingMoves.precompute_advisor_moves()
    elephant_mm = PrecomputingMoves.precompute_elephant_moves()
    pawn_mm = PrecomputingMoves.precompute_pawn_moves()

    @classmethod
    def init_board(cls, board):
        cls.board = board

    @classmethod
    def load_moves(cls, generate_quiets=True) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible moves
        """
        cls.generate_quiets = generate_quiets
        cls.moves = []
        cls.init()
        cls.calculate_attack_data()
        cls.generate_rook_moves()
        cls.generate_cannon_moves()
        cls.generate_pawn_moves()
        cls.generate_horse_moves()
        cls.generate_advisor_moves()
        cls.generate_elephant_moves()
        cls.generate_king_moves()
        return cls.moves
    
    @classmethod
    def init(cls):
        """
        Initializes data used for move generation
        """
        try:
            # cls.moving_king = next(iter(cls.board.piece_lists[cls.board.moving_color][Piece.king]))
            # cls.opponent_king = next(iter(cls.board.piece_lists[cls.board.opponent_color][Piece.king]))
            cls.moving_king = cls.board.piece_lists[cls.board.moving_color][Piece.king][0]
            cls.opponent_king = cls.board.piece_lists[cls.board.opponent_color][Piece.king][0]
        except StopIteration:
            print("invalid move detected")
            print(cls.board.load_fen_from_board())
            cls.board.get_previous_configs(6)
        cls.moves = []

        cls.attack_map = set()
        
        # Swquares that would serve as screen for a threatening cannon
        cls.illegal_squares = set()
        cls.pinned_squares = set()
        # Number of checks
        cls.checks = 0
        # Used for tracking the number of checks a square would block if moved to
        cls.block_check_hash = {}
        # Square used to denote a checking cannon if existing
        cls.checking_cannon_square = None
        # squares occupied by friendly pieces that are part of two pieces blocking a cannon check that can't
        # capture the other piece of double block as it would rearrange the double block into single screen, resulting in check
        cls.double_screens = set()
        # Sqaure of friendly piece that serves as screen for a checking cannon, 
        # whose movement away from check-ray would resolve th check
        cls.cause_cannon_defect = None

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
        :return: precise direction index 0 to 4 between two squares from square_1's perspective
        """
        file_1, rank_1 = cls.board.get_file_and_rank(square_1)
        file_2, rank_2 = cls.board.get_file_and_rank(square_2)
        d_file = file_2 - file_1
        d_rank = rank_2 - rank_1
        if d_file and d_rank or not d_file and not d_rank:
            return None
        # On same file
        if not d_file and d_rank:
            d_rank_norm = d_rank // abs(d_rank)
            return cls.dir_offsets.index(d_rank_norm * 9)
        # On same rank
        d_file_norm = d_file // abs(d_file)
        return cls.dir_offsets.index(d_file_norm)

    @classmethod
    def estimate_dir_idx(cls, square_1, square_2):
        """
        :return: roughly estimated direction index 0 to 4 between two squares from square_1's perspective
        NOTE: Not used right now
        """
        file_1, rank_1 = cls.board.get_file_and_rank(square_1)
        file_2, rank_2 = cls.board.get_file_and_rank(square_2)
        d_file = file_2 - file_1
        d_rank = rank_2 - rank_1
        # On same file
        if abs(d_file) < abs(d_rank):
            d_rank_norm = d_rank // abs(d_rank)
            return cls.dir_offsets.index(d_rank_norm * 9),
        # On same rank
        if abs(d_rank) < abs(d_file):
            d_file_norm = d_file // abs(d_file)
            return cls.dir_offsets.index(d_file_norm),
            
        return cls.dir_offsets.index(d_rank // abs(d_rank) * 9), cls.dir_offsets.index(d_file // abs(d_file))

    @staticmethod
    def get_slope(d_1, d_2):
        """
        NOTE: Not used right now
        """
        return d_2 / d_1


    @classmethod
    def generate_king_moves(cls) -> None:
        current_square = cls.moving_king

        target_squares = cls.king_mm[cls.board.moving_side][current_square]
        for target_square in target_squares:
            target_piece = cls.board.squares[target_square]
            if Piece.is_color(target_piece, cls.board.moving_color):
                continue
            if target_square in cls.attack_map:
                continue
            cls.moves.append((current_square, target_square))
            

    @classmethod
    def generate_rook_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal rook moves
        """
        for current_square in cls.board.piece_lists[cls.board.moving_color][Piece.rook]:
            is_pinned = cls.is_pinned(current_square)
            if cls.checks and is_pinned:
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect

            rook_mm = cls.orthogonal_mm[current_square]
            # Going through chosen direction indices
            for dir_idx, squares_in_dir in rook_mm.items():
                if is_pinned and not cls.moves_along_ray(cls.moving_king, current_square, dir_idx):
                    continue
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in squares_in_dir:
                    target_piece = cls.board.squares[target_square]
                    # If target_piece is friendly, go to next direction
                    if Piece.is_color(target_piece, cls.board.moving_color):
                        break
                    if target_square in cls.illegal_squares:
                        continue
                    # Because all squares between the rook and cannon (inclusive) are in block_check_hash and
                    # current square is avoids_cannon_check, the number of checks blocked would be 2, not 1
                    # so it skips moves between cannon and rook, but would also skip the capture of checking cannon
                    # Thus, if rook is screen for checking cannon and captures it, increment the number of checks by 1
                    # => condition 2 == 1 becomes 2 == 2
                    captures_checking_cannon = avoids_cannon_check and cls.checking_cannon_square == target_square
                    blocks_all_checks = cls.blocks_all_checks(current_square, target_square, captures_checking_cannon)
                    
                    # If it's quiescene search and move isn't a capture, continue
                    if not cls.generate_quiets and not target_piece:
                        continue

                    if blocks_all_checks:    
                        cls.moves.append((current_square, target_square))
                        
                    # If piece on target square and not friendly, go to next direction
                    if target_piece:
                        break
                    # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                    if blocks_all_checks and cls.checks and not avoids_cannon_check:
                        break

    @classmethod
    def generate_pawn_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal pawn moves
        """
        # Looping over friendly pawns
        for current_square in cls.board.piece_lists[cls.board.moving_color][Piece.pawn]:
            is_pinned = cls.is_pinned(current_square)
            if cls.checks and is_pinned:
                break
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            target_squares = cls.pawn_mm[cls.board.moving_side][current_square]

            for target_square in target_squares:
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
                    continue
                if target_square in cls.illegal_squares:
                    continue
                dir_idx = cls.dir_offsets.index(target_square - current_square)
                if is_pinned and not cls.moves_along_ray(cls.moving_king, current_square, dir_idx):
                    continue
                # Because all squares between the pawn and cannon (inclusive) are in block_check_hash and
                # current square is avoids_cannon_check, the number of checks blocked would be 2, not 1
                # so it skips moves between cannon and pawn, but would also skip the capture of checking cannon
                # Thus, if pawn is screen for checking cannon and captures it, increment the number of checks by 1
                # => condition 2 == 1 becomes 2 == 2
                captures_checking_cannon = cls.checking_cannon_square == target_square
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square, captures_checking_cannon)
                if not blocks_all_checks:
                    continue
                # This guard clause is rarely True, so put it last to avoid unnecessary checks
                if not cls.generate_quiets and not target_piece:
                    continue
        
                cls.moves.append((current_square, target_square))
                # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and cls.checks and not avoids_cannon_check:
                    break
    
    @classmethod
    def get_elephant_block(cls, elephant, target_square):
        d_file, d_rank = cls.board.get_dists(target_square, elephant)
        block = elephant + d_rank // 2 * 9 + d_file // 2 
        return block

    @classmethod
    def generate_elephant_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal elephant moves
        """
        for current_square in cls.board.piece_lists[cls.board.moving_color][Piece.elephant]:
            if cls.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            
            for target_square in cls.elephant_mm[cls.board.moving_side][current_square]:
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
                    continue
                
                blocking_square = cls.get_elephant_block(current_square, target_square)
                if cls.board.squares[blocking_square]:
                    continue

                if target_square in cls.illegal_squares:
                    continue
                
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                # If it's quiescene search and move isn't a capture, continue
                if not cls.generate_quiets and not target_piece:
                    continue
                cls.moves.append((current_square, target_square))

                # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and cls.checks and not avoids_cannon_check:
                    break

    @classmethod
    def generate_advisor_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal advisor moves
        """
        for current_square in cls.board.piece_lists[cls.board.moving_color][Piece.advisor]:
            if cls.is_pinned(current_square):
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            target_squares = cls.advisor_mm[cls.board.moving_side][current_square]

            for target_square in target_squares:
                target_piece = cls.board.squares[target_square]
                if Piece.is_color(target_piece, cls.board.moving_color):
                    continue

                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                if target_square in cls.illegal_squares:
                    continue
                # If it's quiescene search and move isn't a capture, continue
                if not cls.generate_quiets and not target_piece:
                    continue

                cls.moves.append((current_square, target_square))
                
                 # If this move blocks check, other moves can't, unless it moves the piece away from cannon check ray
                if blocks_all_checks and cls.checks and not avoids_cannon_check:
                    break

    @staticmethod
    def get_horse_block(current_square, target_square):
        d_rank = target_square // 9 - current_square // 9
        d_file = target_square % 9 - current_square % 9

        if abs(d_rank) > abs(d_file):
            return current_square + d_rank // 2 * 9
        return current_square + d_file // 2

    @classmethod
    def generate_horse_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal horse moves
        """
        for current_square in cls.board.piece_lists[cls.board.moving_color][Piece.horse]:
            if cls.is_pinned(current_square):
                continue
            horse_moves = cls.horse_mm[current_square]

            # legal_moves = list(filter(lambda move: move in illegal_moves, legal_moves))
            for move in horse_moves:
                target_square = move[1]
                target_piece = cls.board.squares[target_square]
                # If it's quiescene search and move isn't a capture, continue
                if Piece.is_color(target_piece, cls.board.moving_color):
                    continue
                blocking_square = cls.get_horse_block(current_square, target_square)
                if cls.board.squares[blocking_square]:
                    continue
                if target_square in cls.illegal_squares:
                    continue
                # If there's a check (or multiple)
                # Only proceed if num of checks the moves blocks is equivalent to total num of checks
                blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                if not blocks_all_checks:
                    continue
                if not cls.generate_quiets and not target_piece:
                    continue
                cls.moves.append((current_square, target_square))
                
    @classmethod
    def generate_cannon_moves(cls) -> None:
        """
        extends Legal_move_generator.moves with legal cannon moves
        """
        for current_square in cls.board.piece_lists[cls.board.moving_color][Piece.cannon]:
            is_pinned = cls.is_pinned(current_square)
            if cls.checks and is_pinned:
                continue
            avoids_cannon_check = current_square == cls.cause_cannon_defect
            cannon_attack_map = cls.orthogonal_mm[current_square]
            is_double_screen = current_square in cls.double_screens
            for dir_idx, targets_in_dir in cannon_attack_map.items():
                if is_pinned and not cls.moves_along_ray(cls.moving_king, current_square, dir_idx):
                    continue

                in_attack_mode = False
                target_piece = False
                # "Walking" in direction using direction offsets
                for target_square in targets_in_dir:

                    if cls.board.squares[target_square] and not in_attack_mode:
                        # If cannon is pinned by opponent rook, it can't capture by using the pinning 
                        # rook or the friendly king as screen, as it would place king in check
                        if is_pinned and not is_double_screen:
                            break
                        # Cannon is the first screen between the opponent cannon and friendly king, making it 
                        # illegal to use opponent cannon as screen. Since the opponent cannon would be the first
                        # piece to come across as attack mode is off, we know that if it's in double screens, 
                        # it must be the first one
                        if Piece.is_piece(cls.board.squares[target_square], cls.board.opponent_color, Piece.cannon) and is_double_screen:
                            break
                        in_attack_mode = True
                        continue

                    if in_attack_mode:
                        target_piece = cls.board.squares[target_square]
                        # if target square is empty, continue
                        if not target_piece:
                            continue
                        # If target_piece is friendly, go to next direction
                        if Piece.is_color_no_check(target_piece, cls.board.moving_color):
                            break
                    
                    blocks_all_checks = cls.blocks_all_checks(current_square, target_square)
                    if not blocks_all_checks:
                        if target_piece:
                            break
                        continue
                    
                    # Can't move to or capture pieces on squares that would result in check
                    if target_square in cls.illegal_squares:
                        continue
                    # If it's quiescene search and move isn't a capture, continue
                    if not cls.generate_quiets and not target_piece:
                        continue
                    cls.moves.append((current_square, target_square))
                    
                    # Move was a capture, can't move further in this direction 
                    if target_piece:
                        break
                    if blocks_all_checks and cls.checks and not avoids_cannon_check:
                        break



#-------------------------------------------------------------------------------
#-------The part below is for calculating pins, checks, double cheks etc.-------
#-------------------------------------------------------------------------------

    @classmethod
    def first_two_in_ray(cls, square_1, square_2, dir_idx):
        """
        :return: the first square between square_1 and square_2 if the number of squares separating them is 1
        :param square_1: where the ray counting the number of squares starts
        """
        dist = abs(square_1 - square_2) // 9
        offset = cls.dir_offsets[dir_idx]
        squares = []
        for step in range(dist - 1):
            square = square_1 + offset * (step + 1)
            piece = cls.board.squares[square]
            if not piece:
                continue
            # Second piece to come across
            if squares:
                return -1
            squares.append(square)
            continue
            
        return squares

    @classmethod
    def flying_general(cls):
        # Opponent king can only pose a threat if it's file's dist to friendly king's file is exactly 1
        moving_king_file = cls.moving_king % 9
        opponent_king_file = cls.opponent_king % 9
        flying_general_threat = abs(moving_king_file - opponent_king_file) < 2
        if not flying_general_threat:
            return
        moving_king_rank = cls.moving_king // 9 
        dir_idx = cls.board.moving_side * 2
        dist_kings = abs(moving_king_rank - cls.opponent_king // 9)
        offset = cls.dir_offsets[dir_idx]
        block = None
        for step in range(dist_kings):
            square = cls.opponent_king + offset * (step + 1)
            piece = cls.board.squares[square]

            if not piece:
                continue
            # Opponent piece blocks any pins, but can't be captured 
            # by friendly king as opponent king's defending it
            if Piece.is_color_no_check(piece, cls.board.opponent_color):
                if not block:
                    cls.attack_map.add(square)
                return

            # Friendly king
            if Piece.is_type_no_check(piece ,Piece.king):
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
        flying_general_square = moving_king_rank * 9 + opponent_king_file
        cls.attack_map.add(flying_general_square)

        #------------------------------------MISTAKE DOCUMENTATION--------------------------------
        # THIS WAS A GOOD IDEA, EXCEPT FOR THE FACT THAT IT WAS A BAD IDEA.
        # THE VERSION ABOVE IS MUCH FASTER, AS IT INTERRUPTS THE CHECK RAY EARLIER
        
        # blocking_squares = cls.first_two_in_ray(cls.opponent_king, cls.moving_king, dir_idx)
        # if blocking_squares == -1:
        #     return

        # if blocking_squares:
        #     # Turning list into integer
        #     blocking_squares = blocking_squares.pop()
        #     blocking_piece = cls.board.squares[blocking_squares]

        #     # Opponent piece: blocks any pins, but can't be captured 
        #     # by friendly king as opponent king's defending it
        #     if Piece.is_color(blocking_piece, cls.board.opponent_color):
        #         cls.attack_map.add(blocking_squares)
        #         return
        #     # Friendly piece: gets pinned if kings are on same rank
        #     if opponent_king_file == moving_king_file:
        #         cls.pinned_squares.add(blocking_squares)
        #     return
        # # Number of pieces between kings is 0
        # # If there're no pieces between opponent king and opposite edge of board
        # # friendly king can't move to the opponent king's file
        # moving_king_rank = cls.moving_king // 9 
        # flying_general_square = moving_king_rank * 9 + opponent_king_file
        # cls.attack_map.add(flying_general_square)
        
    @classmethod
    def calculate_horse_attack_data(cls) -> None:
        opponent_horses = cls.board.piece_lists[cls.board.opponent_color][Piece.horse]
        for square in opponent_horses:
            if cls.board.get_manhattan_dist(square, cls.moving_king) > 4:
                continue
            for move in cls.horse_mm[square]:
                target_square = move[1]
               
                # --------------------------------MISTAKE DOCUMENTATION-----------------------------------
                # Not adding squares to the attack map if they're occupied by an opponent piece allows 
                # the king to make pseudo-legal capture to squares that can be attacked by opponent pieces
                # Bugs like these are really valuable and virtually inevitable in complex applications 
                # if Piece.is_color(cls.board.squares[target_square], cls.opponent):
                #     continue
                # -----------------------------------------------------------------------------------------

                block_square = cls.get_horse_block(square, target_square)
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
                if Piece.is_color_no_check(block_piece, cls.board.opponent_color) or not is_move_check:
                    continue
                # If blocked by friendly piece and move would result in check, it's pinned
                cls.pinned_squares.add(block_square)

    @classmethod
    def exclude_king_moves(cls):
        king_mm = cls.king_mm[cls.board.moving_side][cls.moving_king]
        # Filtering out squares occupied by friendly pieces
        king_mm = list(filter(lambda target: not Piece.is_color(cls.board.squares[target], cls.board.moving_color), king_mm))
        if not cls.generate_quiets:
            king_mm = list(filter(lambda target: cls.board.squares[target], king_mm))
        # Looping over possible king moves
        for target_square in king_mm:
            if target_square in cls.attack_map:
                continue
            for rook in cls.board.piece_lists[cls.board.opponent_color][Piece.rook]:
                attack_dir_idx = cls.get_orth_dir_idx(rook, target_square)
                # If cannon could threaten king's move, generate attack ray
                if attack_dir_idx != None:
                    cls.generate_rook_attack_ray(rook, attack_dir_idx)

        king_mm = list(filter(lambda target: target not in cls.attack_map, king_mm))
        for target_square in king_mm:
            if target_square in cls.attack_map:
                continue
            # Looping over opponent cannons
            for cannon in cls.board.piece_lists[cls.board.opponent_color][Piece.cannon]:
                attack_dir_idx = cls.get_orth_dir_idx(cannon, target_square)
                # If cannon could threaten king's move, generate attack ray
                if attack_dir_idx != None:
                    cls.generate_cannon_attack_ray(cannon, attack_dir_idx)

        cls.generate_pawn_attack_data(king_mm)

        # -----------------------------------MISTAKE DOCUMENTATION-------------------------------------------
        # for rook in cls.board.piece_lists[cls.board.opponent_color][Piece.rook]:
        #     dists = cls.board.get_2d_dists(rook, cls.moving_king)
        #     min_dist = min(*dists)
        #     # If minimum distance among the two axes is greater than 1, rook can pose no threat to king
        #     if min_dist > 1:
        #         continue
        #     for attack_dir_idx in cls.estimate_dir_idx(rook, cls.moving_king):
        #         # The minimum distance among the two axes is 1
        #         if not min_dist:
        #             # The minimum distance among the two axes is 0
        #             cls.get_rook_imposed_limits(rook, attack_dir_idx)
        #         cls.generate_rook_attack_ray(rook, attack_dir_idx)
        # -------------------------------------------------------------------------------------------------------

    @classmethod
    def generate_pawn_attack_data(cls, king_moves):
        for pawn in cls.board.piece_lists[cls.board.opponent_color][Piece.pawn]:
            mhd = cls.board.get_manhattan_dist(pawn, cls.moving_king)
            if mhd > 2:
                continue
            for attacked_square in cls.pawn_mm[cls.board.opponent_side][pawn]:
            # Pawn is posing a threat to friendly king
                if attacked_square in king_moves:
                    cls.attack_map.add(attacked_square)
                    continue
                if attacked_square == cls.moving_king:
                    cls.checks += 1
                    cls.block_check_hash[pawn] = cls.block_check_hash.get(pawn, 0) + 1

    @classmethod
    def confine_movement(cls) -> None:
        for cannon in cls.board.piece_lists[cls.board.opponent_color][Piece.cannon]:
            attack_dir_idx = cls.get_orth_dir_idx(cannon, cls.moving_king)
            # If cannon could threaten king's move, generate attack ray
            if attack_dir_idx != None:
                cls.get_cannon_imposed_limits(cannon, attack_dir_idx)
        for rook in cls.board.piece_lists[cls.board.opponent_color][Piece.rook]:
            attack_dir_idx = cls.get_orth_dir_idx(rook, cls.moving_king)
            # If cannon could threaten king's move, generate attack ray
            if attack_dir_idx != None:
                cls.get_rook_imposed_limits(rook, attack_dir_idx)     


    @classmethod
    def generate_cannon_attack_ray(cls, square, dir_idx):
        """
        generates attack map along ray of given direction from given square
        """
        attack_ray = cls.orthogonal_mm[square][dir_idx]
        screen = False
        double_block = False
        for attacking_square in attack_ray:
            piece = cls.board.squares[attacking_square]
            # attacking square is occupied
            # Cannon is in capture mode
            if screen:
                cls.attack_map.add(attacking_square)
            if piece:
                if Piece.is_piece(piece, cls.board.moving_color, Piece.king):
                    if screen: 
                        continue
                    return
                double_block = screen
                screen = True

            if double_block:
                return

    @classmethod
    def generate_rook_attack_ray(cls, square, dir_idx) -> None:
        attack_ray = cls.orthogonal_mm[square][dir_idx]
        for attacking_square in attack_ray:
            piece = cls.board.squares[attacking_square]
            cls.attack_map.add(attacking_square)
            # Attacking square occupied, break
            if piece:
                if Piece.is_piece(piece, cls.board.moving_color, Piece.king):
                    continue
                break

    @classmethod
    def get_cannon_imposed_limits(cls, cannon, dir_idx):
        """
        Adds pins and illegal squares to instance variables "pinned_squares" and "illegal_squares" 
        :param cannon: square occupied by the cannon imposing the limits
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

                    # -------------------------MISTAKE DOCUMENTATION----------------------------
                    # This is no viable solution to double screen capturing, because we
                    # only want to limit the friendly screen from capturing opponent screen
                    # if not friendly_screens:
                    #     continue
                    # for screen in opponent_screens:
                    #     cls.block_check_hash[screen] = cls.block_check_hash.get(screen, 0) - 1
                    #----------------------------------------------------------------------------

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
            if Piece.is_color_no_check(piece, cls.board.moving_color):
                friendly_screens.add(attacking_square)

            # First piece: block
            # second piece: double block    
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
            if Piece.is_color_no_check(piece, cls.board.moving_color):
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


    @classmethod
    def get_legal_moves(cls, square):
        moves_from_square = list(filter(lambda move: move[0] == square, cls.moves))
        return moves_from_square

    @classmethod
    def get_legal_targets(cls, square):
        moves_from_square = cls.get_legal_moves(square)
        targets = list(map(lambda move: move[1], moves_from_square))
        return targets