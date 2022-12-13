"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from core.Engine.AI import Dfs

class AIPlayer:
    SEARCH_DEPTH = 6
    @classmethod
    def load_move(cls, board):
        move = Dfs.multiprocess_search(cls.SEARCH_DEPTH, board)
        return move

    @classmethod
    def make_move(cls, board):
        move = cls.load_move()
        board.make_move(move)