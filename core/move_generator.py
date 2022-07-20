from piece import Piece

class Legal_move_generator:
    # Orthogonal and diagonal offsets of board represented in one dimension
    dir_offsets = [-9, 1, 9, -1, -8, 10, 8, -10]

    def __init__(self, board) -> None:
        self.dir_offsets.extend(self.jumps_from_orthogonal_offsets())
        
        self.dist_to_edge = self.precompute_dists()

        # Precalculating move maps
        self.king_moves = self.precompute_king_moves()
        self.rook_moves = self.precompute_rook_moves()
        self.horse_moves = self.precompute_horse_moves()
        self.advisor_moves = self.precompute_advisor_moves()
        self.elephant_moves = self.precompute_elephant_moves()
        self.pawn_moves = self.precompute_pawn_moves()

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
    def jumps_from_orthogonal_offsets() -> list:
        """
        :return: a list of integers representing the offsets of a horse jump,
        ordered in a way where precompute_horse_moves() can use them to exclude
        illegal moves blocked by a piece
        """
        horse_offsets = []
        dir_offsets = Legal_move_generator.dir_offsets[:4] + [-9]

        for dir_index in range(4):
            second_dir_idx = dir_index + 1

            for steps in range(2):
                first_dir_steps = 2 - steps
                second_dir_steps = 1 + steps
                new_offset = dir_offsets[dir_index] * first_dir_steps + dir_offsets[second_dir_idx] * second_dir_steps
                horse_offsets.append(new_offset)
        return horse_offsets
    

    @staticmethod
    def precompute_king_moves() -> list:
        """
        :return: a list of one dictionary for one side fo the board each, containing 
        all start indices as keys and the possible targets of those positions as value\n
        output form : [{int : [int, int...], int: [int]...}, {...}]
        """
        king_moves = []
        offsets_for_rank = [[9], [9, -9], [-9]]
        offsets_for_file = [[1], [1, -1], [-1]]
        
        # Precalculate offsets for each position in palace 
        # by combining each rank's offset with that of every file
        offsets = []
        for hor in offsets_for_rank:
            for ver in offsets_for_file:
                offsets.append(hor + ver)

        # These are the top-left corners of each palace
        start_squares = [66 , 3]
        #O-----+
        #|\ | /|
        #|--+--| Top-left marked by an "O"
        #|/ | \|
        #+-----+
        
        for color in range(2):
            king_moves.append({})
            # Iterating through each palace
            for row in range(3):
                for col in range(3):
                    current_square = start_squares[color] + row * 9 + col
                    # Get the offsets for the current position in the palace
                    dir_idx = row * 3 + col
                    for offset in offsets[dir_idx]:
                        target_square = current_square + offset
                        # Adding target square to current color at current square
                        king_moves[color][current_square] = king_moves[color].get(current_square, []) + [target_square]
        return king_moves


    def precompute_rook_moves(self) -> list:
        """
        :return: a list of lists containing the rook move-target indices of all squares
        """
        target_squares = []
        for square in range(90):
            target_squares.append({})
            # Looping over orthogonal directions
            for dir_idx in range(4):
                offset = self.dir_offsets[dir_idx]
                # "Walking" in direction using direction offsets
                for step in range(self.dist_to_edge[square][dir_idx]):
                    target_square = square + offset * (step + 1)
                    target_squares[square][dir_idx] = target_squares[square].get(dir_idx, []) + [target_square]
        return target_squares


    def precompute_horse_moves(self) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible horse moves
        """
        # (not accounting for move blocks, )

        horse_offsets = self.dir_offsets[8:16]
        horse_moves = []
        for square in range(90):
            horse_moves.append([])
            for dir_index in range(8):
                # board is a 1d array, so if jump is outside of file (illegal), it will just jump to new rank
                # fix to illegal jumps perceived as legal by computer 
                target_square = square + horse_offsets[dir_index]
                target_rank = target_square // 9
                target_file = target_square - target_rank * 9
                current_rank = square // 9
                current_file = square - current_rank * 9
                max_dist = max(abs(current_rank - target_rank), abs(current_file - target_file))
                if max_dist > 2 or not -1 < target_square < 90:
                    continue
                horse_moves[square].append((square, target_square))

        return horse_moves


    def precompute_advisor_moves(self) -> list:
        """
        :return: a list of one dictionary for one side fo the board each, containing 
        all start indices as keys and the possible targets of those positions as value\n
        output form : [{int : [int, int...], int: [int]...}, {...}]
        """
        advisor_moves = []
        #+-----+
        #|\ | /|
        #|--O--| the O marks the middle
        #|/ | \| of the so-called palace
        #+-----+

        palace_middle_squares = [89 - 13, 13]
        for color in range(2):
            advisor_moves.append({})
            middle_square = palace_middle_squares[color]
            # seperate moves for each color
            for dir_index in range(4, 8):

                dir_offset = self.dir_offsets[dir_index]
                target_square = middle_square + dir_offset

                # All of the target squares' only move is back to the 
                # palace_middle_square, so add move to target_square and back
                advisor_moves[color][middle_square] = advisor_moves[color].get(middle_square, []) + [target_square]
                advisor_moves[color][target_square] = advisor_moves[color].get(target_square, []) + [middle_square]
        return advisor_moves


    def precompute_pawn_moves(self) -> list:
        """
        :return: a list of one dictionary for one side fo the board each, containing 
        all start indices as keys and the possible targets of those positions as value\n
        output form : [{int : [int, int...], int: [int]...}, {...}]
        """
        pawn_moves = []
        offset_push_move = [-9, 9]

        # Used to determine whether pawn can push foward
        is_foward_move = (lambda rank: 0 < rank < 7, lambda rank: 9 > rank > 2)
        # Used to determine whether pawn can move sideways (after crossing river)
        is_river_crossed = (lambda rank: rank < 5, lambda rank: rank > 4)

        for color in range(2):
            pawn_moves.append({})
            for square in range(90):
                rank = square // 9
                river_crossed = is_river_crossed[color](rank)
                foward_move = is_foward_move[color](rank)
                if river_crossed:
                    for dir_idx in [1, 3]:
                        if self.dist_to_edge[square][dir_idx] < 1:
                            continue
                        offset = self.dir_offsets[dir_idx]
                        pawn_moves[color][square] = pawn_moves[color].get(square, []) + [square + offset]
                if foward_move:
                    offset = offset_push_move[color]
                    pawn_moves[color][square] = pawn_moves[color].get(square, []) + [square + offset]
        return pawn_moves


    def precompute_elephant_moves(self) -> list:
        """
        :return: a list of one dictionary for one side fo the board each, containing 
        all start indices as keys and the possible targets of those positions as value\n
        output form : [{int : [int, int...], int: [int]...}, {...}]
        """
        elephant_moves = []
        offsets = self.dir_offsets[4:8]

        # if the normal range() function is used for both sides, is_river_crossed 
        # will be True instantly when color = 0, so backwards from rank 9 as 9 < 5 is False
                                # Equivalent to "reversed(range(start + 1, stop + 1, step))"
        iteration_sequence = (lambda start, stop, step: range(stop - 1, start - 1, -step),
                            lambda start, stop, step: range(start, stop, step))
        # Used to determine whether move or current position crosses river (in which case it's illegal)
        is_river_crossed = (lambda rank: rank < 5, lambda rank: rank > 4)

        for color in range(2):
            elephant_moves.append({})
            for rank in iteration_sequence[color](0, 10, 2):
                # If current position crossed river, go to next color
                if is_river_crossed[color](rank):
                    break

                for file in range(0, 9, 2):
                    square = rank * 9 + file
                    for offset in offsets:
                        target_square = square + offset * 2
                        # Avoiding moves to negative squares
                        if not -1 < target_square < 90:
                            continue

                        target_rank = target_square // 9
                        move_crosses_river = is_river_crossed[color](target_rank)
                        if move_crosses_river:
                            continue
                        
                        target_file = target_square % 9
                        # Avoiding moves out of bounds, see "precompute_horse_moves()"
                        max_dist = max(abs(target_rank - rank), abs(target_file - file))
                        if max_dist > 2:
                            continue
                        elephant_moves[color][square] = elephant_moves[color].get(square, []) + [target_square]
        return elephant_moves


    def generate_king_moves(self) -> None:
        current_square = self.friendly_king

        target_squares = self.king_moves[self.friendly][current_square]
        for target_square in target_squares:
            if target_square in self.attack_map:
                continue
            target_piece = self.board.squares[target_square]
            # Checking if target_piece is friendly while avoiding Errors 
            # (piece is equal to 0 when target_square is empty) so piece[0] would raise TypeError
            is_friendly = target_piece[0] == self.friendly if target_piece else False
            if is_friendly:
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
                is_friendly = target_piece[0] == self.friendly if target_piece else False
                if is_friendly:
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
                is_friendly = target_piece[0] == self.friendly if target_piece else False
                if is_friendly:
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
                is_friendly = target_piece[0] == self.friendly if target_piece else False
                if is_friendly:
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
                is_friendly = target_piece[0] == self.friendly if target_piece else False
                if is_friendly:
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
                    is_friendly = target_piece[0] == self.friendly if target_piece else False
                    # If target_piece is friendly, go to next direction
                    if is_friendly:
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