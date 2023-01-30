"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from core.engine import LegalMoveGenerator
class GameManager:
    """
    Handles states of the game (e.g. Checkmate, Stalemate...)
    """
    checkmate = False
    stalemate = False
    gameover = False
    fifty_move_counter = 0

    @classmethod
    def reset_mate(cls):
        cls.checkmate = False
        cls.stalemate = False
        cls.gameover = False

    @classmethod
    def check_game_state(cls):
        # Load moves for next player
        moves = LegalMoveGenerator.moves
        if not len(moves):
            cls.gameover = True
            cls.checkmate = bool(LegalMoveGenerator.checks)
            cls.stalemate = not cls.checkmate

    @classmethod
    def increment_move_counter(cls):
        cls.fifty_move_counter += 1

    @classmethod
    def reset_move_counter(cls):
        cls.fifty_move_counter = 0
        