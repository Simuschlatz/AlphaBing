"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
import csv
import os
from core.Engine.AI import Dfs
import pandas as pd
"""
1. write into csv file --
2. writes board list and eval of board to csv file --
3. check for redundant storing of identical lists --
4. ai vs ai for random boards
"""

class Data_generator:
    dir_path = "core/Engine/AI/SLEF"
    filepath = os.path.join(dir_path, "eval_data.csv")
    num_plies_ahead = 1
    print(filepath)
    def __init__(self, board):
        self.board = board
        try:
            self.training_data = pd.read_csv(self.filepath)

        except pd.errors.EmptyDataError:
            labels = self.generate_labels()
            self.append_row_csv(self.filepath, labels)
            self.training_data = pd.DataFrame(columns=labels)
        self.boards_hash = {tuple(self.training_data.iloc[i][:-1]) for i in range(len(self.training_data))}
        print(self.training_data)

    def generate_labels(self):
        labels = [f"s{i}" for i in range(1, 91)] + ["eval"]
        return labels

    @staticmethod
    def append_row_csv(path, data):
        # open the file in the write mode
        with open(path, 'a') as f:
            # create the csv writer
            writer = csv.writer(f)
            # write a row to the csv file
            writer.writerow(data)

    @staticmethod
    def append_rows_csv(path, data):
        # open the file in the write mode
        with open(path, 'a') as f:
            # create the csv writer
            writer = csv.writer(f)
            # write a row to the csv file
            writer.writerows(data)

    @staticmethod
    def parse_board_config(squares):
        squeezed_squares = squares[:]
        for i, square in enumerate(squares):
            if type(square) != tuple:
                continue
            piece_color, piece_type = square
            flattened = piece_color * 7 + piece_type + 1
            squeezed_squares[i] = flattened
        return tuple(squeezed_squares)

    def is_redundant(self, board_config):
        return board_config in self.boards_hash

    def store_training_data(self):
        board_config = self.parse_board_config(self.board.squares)
        if self.is_redundant(board_config):
            print("Redundant")
            return
        self.boards_hash.add(board_config)
        row = list(board_config)
        best_eval = Dfs.get_best_eval(2)
        row.append(best_eval)
        # num_rows, _ = self.training_data.shape
        # self.training_data.loc[num_rows] = row
        self.append_row_csv(self.filepath, row)