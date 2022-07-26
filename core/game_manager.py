class Game_manager:
    """
    Handles states of the game (e.g. Checkmate, Stalemate...)
    """
    def __init__(self):
        self.checkmate = False
        self.stalemate = False
        self.fifty_move_counter = 0

    def increment_move_counter(self):
        self.fifty_move_counter += 1

    def reset_move_counter(self):
        self.fifty_move_counter = 0
