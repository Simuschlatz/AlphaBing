"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from collections import defaultdict, deque
from core.Engine import Board
class PrecomputingMoves:
    """
    precomputes all pseudo-legal moves for all pieces at all possible positions
    """
    @classmethod
    def init(cls):
        # Orthogonal and diagonal offsets of board represented in one dimension
        cls.dir_offsets = [-9, 1, 9, -1, -8, 10, 8, -10]
        cls.dist_to_edge = cls.precompute_dists()
        # Horse / knight offsets, also appended to direction offsets
        cls.horse_offsets = cls.append_horse_offsets()
        # print(cls.horse_offsets)
        cls.action_space_vector = []
        
        # Precalculating move maps
        cls.king_mm = cls.get_king_move_map()
        cls.orthogonal_mm = cls.get_orthogonal_move_map()
        cls.horse_mm = cls.get_horse_move_map()
        cls.advisor_mm = cls.get_advisor_move_map()
        cls.elephant_mm = cls.get_elephant_move_map()
        cls.pawn_mm = cls.get_pawn_move_map()

        cls.action_space = len(cls.action_space_vector)
        cls.move_index_hash = {move: index for index, move in enumerate(cls.action_space_vector)}
        # exit(0)

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
                    left
                ]
                distances.append(dist)
        return distances

    @classmethod
    def append_horse_offsets(cls) -> list:
        """
        :return: a list of integers representing the offsets of a horse jump,
        ordered in a way where move_generator.generate_horse_moves() can use
        them to exclude illegal moves blocked by a piece
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
    def get_king_move_map() -> list:
        """
        :return: a list of one hash map for each side of the board, containing 
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
        start_squares = [3, 66]
        #O-----+
        #|\ | /|
        #|--+--| Top-left marked by an "O"
        #|/ | \|
        #+-----+
        
        for side in range(2):
            king_moves.append({})
            # Iterating through each palace
            for row in range(3):
                for col in range(3):
                    current_square = start_squares[side] + row * 9 + col
                    # Get the offsets for the current position in the palace
                    off_idx = row * 3 + col
                    for offset in offsets[off_idx]:
                        target_square = current_square + offset
                        # Adding target square to current side at current square
                        king_moves[side][current_square] = king_moves[side].get(current_square, []) + [target_square]
        return king_moves

    @classmethod
    def get_orthogonal_move_map(cls) -> list:
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
                    cls.action_space_vector.append((square, target_square))
        return target_squares

    @classmethod
    def get_horse_move_map(cls) -> list:
        """
        :return: a list of tuples containing the start and end indices of all possible horse moves
        """
        # (not accounting for move blocks, )

        horse_offsets = cls.dir_offsets[8:16]
        horse_moves = []
        for square in range(90):
            horse_moves.append([])
            for dir_index in range(8):
                target_square = square + horse_offsets[dir_index]
                if not -1 < target_square < 90:
                    continue
                # board is a 1d array, so if jump is outside of file (illegal), it will just jump to new rank
                # This part fixes the problem
                if Board.get_manhattan_dist(square, target_square) > 3:
                    continue
                horse_moves[square].append( target_square)
                cls.action_space_vector.append((square, target_square))
        return horse_moves

    @classmethod
    def get_advisor_move_map(cls) -> list:
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

        palace_middle_squares = [13, 89 - 13]
        for side in range(2):
            advisor_moves.append({})
            middle_square = palace_middle_squares[side]
            # seperate moves for each side
            for dir_index in range(4, 8):

                dir_offset = cls.dir_offsets[dir_index]
                target_square = middle_square + dir_offset

                # All of the target squares' only move is back to the 
                # palace_middle_square, so add move to target_square and back
                advisor_moves[side][middle_square] = advisor_moves[side].get(middle_square, []) + [target_square]
                advisor_moves[side][target_square] = advisor_moves[side].get(target_square, []) + [middle_square]
                if not side: 
                    moves = (middle_square, target_square), (target_square, middle_square)
                    cls.action_space_vector.extend(moves)    
        return advisor_moves

    @classmethod
    def get_pawn_move_map(cls) -> list:
        """
        :return: a list of one hash map for each side of the board, containing 
        all start indices as keys and the possible targets of those positions as value\n
        output form : [{int : [int, int...], int: [int]...}, {...}]
        """
        pawn_moves = []
        offset_push_move = [9, -9]

        # Used to determine whether pawn can push foward
        is_foward_move = (lambda rank: 9 > rank > 2, lambda rank: 0 < rank < 7)
        # Used to determine whether pawn can move sideways (after crossing river)
        is_river_crossed = (lambda rank: rank > 4, lambda rank: rank < 5)

        for side in range(2):
            pawn_moves.append({})
            for square in range(90):
                rank = square // 9
                river_crossed = is_river_crossed[side](rank)
                foward_move = is_foward_move[side](rank)
                if river_crossed:
                    for dir_idx in [1, 3]:
                        if cls.dist_to_edge[square][dir_idx] < 1:
                            continue
                        offset = cls.dir_offsets[dir_idx]
                        pawn_moves[side][square] = pawn_moves[side].get(square, []) + [square + offset]
                if foward_move:
                    offset = offset_push_move[side]
                    pawn_moves[side][square] = pawn_moves[side].get(square, []) + [square + offset]
        return pawn_moves


    @classmethod
    def get_elephant_move_map(cls) -> list:
        elephant_moves = []
        offsets = cls.dir_offsets[4:8]
        # Used to determine whether move or current position crosses river (in which case it's illegal)
        is_river_crossed = (lambda square: square > 44, lambda square: square < 45)

        for side in range(2):
            start_square_stack = deque([87 if side else 2])
            elephant_moves.append(defaultdict(list))
            while start_square_stack:
                # iteratively (could do this recursively as well though) 
                # dfsing the path of elephant, adding all moves on the way
                square = start_square_stack.pop()
                target_squares = elephant_moves[side][square]
                _hash = set(target_squares)
                for off in offsets:
                    target_square = square + 2 * off
                    if not -1 < target_square < 90:
                        continue
                    # Avoiding perpetual "stepping" between two squares by excluding squares already visited
                    if target_square in _hash:
                        continue
                    # Elephant can't cross river
                    move_crosses_river = is_river_crossed[side](target_square)
                    if move_crosses_river:
                        continue
                    # Avoiding moves out of bounds, see "precompute_horse_moves()"
                    if Board.get_manhattan_dist(square, target_square) > 4:
                        continue
                    target_squares.append(target_square)
                    start_square_stack.append(target_square)
                    if not side: cls.action_space_vector.append((square, target_square))
        return list(map(lambda dd: dict(dd), elephant_moves))

    # This is the version prior to the one above. Here the problem wasn't that the method wasn't working, but rather the
    # unnecessary amount of computations it took. It returned a move map for squares where the elephant couldn't even go
    # and hence, also messed up the move vector used to label the ML model
    '''
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
        # will be True instantly when side = 0, so backwards from rank 9 as 9 < 5 is False
                                # Equivalent to "reversed(range(start + 1, stop + 1, step))"
        iteration_sequence = (lambda start, stop, step: range(start, stop, step), 
                            lambda start, stop, step: range(stop - 1, start - 1, -step))
        # Used to determine whether move or current position crosses river (in which case it's illegal)
        is_river_crossed = (lambda rank: rank > 4, lambda rank: rank < 5)
        num_moves_before = len(cls.move_vector)
        for side in range(2):
            elephant_moves.append({})
            for rank in iteration_sequence[side](0, 10, 2):
                # If current position crossed river, go to next side
                if is_river_crossed[side](rank):
                    break
                for file in range(0, 9, 2):
                    # Avoiding the corners
                    if rank + file in {0, 8, 9, 17}:
                        continue
                    # every two collumns in every two rows
                    square = rank * 9 + file
                    for offset in offsets:
                        target_square = square + offset * 2
                        # Avoiding moves to squares outside of board
                        if not -1 < target_square < 90:
                            continue

                        target_rank = target_square // 9
                        move_crosses_river = is_river_crossed[side](target_rank)
                        if move_crosses_river:
                            continue
                        
                        if max(Board.get_abs_dist(square, target_square)) > 2:
                            continue
                        elephant_moves[side][square] = elephant_moves[side].get(square, []) + [target_square]
                        if not side: cls.move_vector.append((square, target_square))
        print(len(cls.move_vector) - num_moves_before)
        return elephant_moves
        '''
