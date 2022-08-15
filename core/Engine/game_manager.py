class Game_manager:
    """
    Handles states of the game (e.g. Checkmate, Stalemate...)
    """
    checkmate = False
    stalemate = False
    fifty_move_counter = 0

    @classmethod
    def reset_game_state(cls):
        cls.checkmate = False
        cls.stalemate = False

    @classmethod
    def increment_move_counter(cls):
        cls.fifty_move_counter += 1

    @classmethod
    def reset_move_counter(cls):
        cls.fifty_move_counter = 0

    @classmethod
    def reset_move_counter(cls):
        cls.fifty_move_counter = 0
