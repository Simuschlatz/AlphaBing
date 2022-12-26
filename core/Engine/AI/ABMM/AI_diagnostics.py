"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""

class Diagnostics:
    @classmethod
    def init(cls):
        cls.depth = 0
        cls.evaluated_nodes = 0
        cls.best_eval = 0
        cls.move = None

