from core.Engine.AI import Dfs
class AI_player:
    SEARCH_DEPTH = 4
    @classmethod
    def load_move(cls):
        move = Dfs.traverse_tree(cls.SEARCH_DEPTH)
        print(f"traversed nodes: {Dfs.searched_nodes}")
        return move