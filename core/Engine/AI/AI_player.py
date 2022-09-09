from core.Engine.AI import Dfs
class AI_player:
    SEARCH_DEPTH = 4
    @classmethod
    def load_move(cls):
        move = Dfs.search(cls.SEARCH_DEPTH)
        return move