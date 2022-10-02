"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
class Tt_entry:
    def __init__(self, zobrist_key, eval, depth) -> None:
        self.zobrist_key = zobrist_key
        self.eval = eval