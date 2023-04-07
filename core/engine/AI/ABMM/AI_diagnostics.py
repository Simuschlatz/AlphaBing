
class Diagnostics:
    @classmethod
    def init(cls):
        cls.depth = 0
        cls.evaluated_nodes = 0
        cls.best_eval = 0
        cls.move = None

