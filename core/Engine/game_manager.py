"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
from core.Engine import Legal_move_generator
class Game_manager:
    """
    Handles states of the game (e.g. Checkmate, Stalemate...)
    """
    checkmate = False
    stalemate = False
    fifty_move_counter = 0

    @classmethod
    def reset_mate(cls):
        cls.checkmate = False
        cls.stalemate = False

    @classmethod
    def check_game_state(cls):
        # Load moves for next player
        moves = Legal_move_generator.moves
        if not len(moves):
            if Legal_move_generator.checks:
                cls.checkmate = True
                return
            cls.stalemate = True

    @classmethod
    def increment_move_counter(cls):
        cls.fifty_move_counter += 1

    @classmethod
    def reset_move_counter(cls):
        cls.fifty_move_counter = 0

    @classmethod
    def reset_move_counter(cls):
        cls.fifty_move_counter = 0
