class Precomputing_moves:

    @classmethod
    def init_constants(cls):
        # Orthogonal and diagonal offsets of board represented in one dimension
        cls.dir_offsets = [-9, 1, 9, -1, -8, 10, 8, -10]
        cls.dist_to_edge = cls.precompute_dists()
        cls.append_horse_offsets()

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

    @classmethod
    def append_horse_offsets(cls) -> list:
        """
        :return: a list of integers representing the offsets of a horse jump,
        ordered in a way where precompute_horse_moves() can use them to exclude
        illegal moves blocked by a piece
        """
        horse_offsets = []
        dir_offsets = cls.dir_offsets[:4] + [-9]

        for dir_index in range(4):
            second_dir_idx = dir_index + 1

            for steps in range(2):
                first_dir_steps = 2 - steps
                second_dir_steps = 1 + steps
                new_offset = dir_offsets[dir_index] * first_dir_steps + dir_offsets[second_dir_idx] * second_dir_steps
                horse_offsets.append(new_offset)
        cls.dir_offsets.extend(horse_offsets)
        return horse_offsets

    @staticmethod
    def precompute_king_moves() -> list:
        """
        :return: a list of one hash mapfor each side of the board, containing 
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

    @classmethod
    def precompute_orthogonal_moves(cls) -> list:
        """
        :return: a list of hash tables containing the direction index as key \n 
        and lists of the according target indices as values
        """
        target_squares = []
        for square in range(90):
            target_squares.append({})
            # Looping over orthogonal directions
            for dir_idx in range(4):
                offset = cls.dir_offsets[dir_idx]
                # "Walking" in direction using direction offsets
                for step in range(cls.dist_to_edge[square][dir_idx]):
                    target_square = square + offset * (step + 1)
                    target_squares[square][dir_idx] = target_squares[square].get(dir_idx, []) + [target_square]
        return target_squares

    @classmethod
    def precompute_horse_moves(cls) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible horse moves
        """
        # (not accounting for move blocks, )

        horse_offsets = cls.dir_offsets[8:16]
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

    @classmethod
    def precompute_advisor_moves(cls) -> list:
        """
        :return: a list of one hash map for each side of the board, containing 
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

                dir_offset = cls.dir_offsets[dir_index]
                target_square = middle_square + dir_offset

                # All of the target squares' only move is back to the 
                # palace_middle_square, so add move to target_square and back
                advisor_moves[color][middle_square] = advisor_moves[color].get(middle_square, []) + [target_square]
                advisor_moves[color][target_square] = advisor_moves[color].get(target_square, []) + [middle_square]
        return advisor_moves

    @classmethod
    def precompute_pawn_moves(cls) -> list:
        """
        :return: a list of one hash mapfor each side of the board, containing 
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
                        if cls.dist_to_edge[square][dir_idx] < 1:
                            continue
                        offset = cls.dir_offsets[dir_idx]
                        pawn_moves[color][square] = pawn_moves[color].get(square, []) + [square + offset]
                if foward_move:
                    offset = offset_push_move[color]
                    pawn_moves[color][square] = pawn_moves[color].get(square, []) + [square + offset]
        return pawn_moves

    @classmethod
    def precompute_elephant_moves(cls) -> list:
        """
        :return: a list of one hash mapfor each side of the board, containing 
        all start indices as keys and the possible targets of those positions as value\n
        output form : [{int : [int, int...], int: [int]...}, {...}]
        """
        elephant_moves = []
        offsets = cls.dir_offsets[4:8]

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
