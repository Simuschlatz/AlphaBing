"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
from core.Engine.AI import Dfs

class AIPlayer:
    SEARCH_DEPTH = 4
    @classmethod
    def load_move(cls):
        move = Dfs.search(cls.SEARCH_DEPTH)
        return move

    @classmethod
    def make_move(cls, board):
        move = cls.load_move()
        board.make_move(move)