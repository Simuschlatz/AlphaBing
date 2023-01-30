"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
import csv
import os
from core.engine.AI.ABMM import Dfs
import pandas as pd

class TrainingDataCollector:
    dir_path = "core/engine/AI/SLEF"
    filepaths = [os.path.join(dir_path, "eval_data_black.csv"), os.path.join(dir_path, "eval_data_red.csv")]
    num_plies_ahead = 3

    def __init__(self, board):
        self.board = board
        self.boards_hash = []
        self.labels = self.generate_labels()
        for filepath in self.filepaths:
            training_data = None
            # File is not empty, meaning its content can be read by pandas
            if os.stat(filepath).st_size > 0:
                training_data = pd.read_csv(filepath)
            else:
                # File is empty, so add the labels and create a data frame 
                self.append_row_csv(filepath, self.labels)
                training_data = pd.DataFrame(columns=self.labels)

            num_rows = len(training_data)
            # Copying all the existing boards, excluding their evals to save memory
            self.boards_hash.append({tuple(training_data.iloc[i][:-1]) for i in range(num_rows)})
            # print(training_data)

    @staticmethod
    def generate_labels():
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
        return board_config in self.boards_hash[self.board.moving_side]

    def store_training_data(self):
        board_config = self.parse_board_config(self.board.squares)
        if self.is_redundant(board_config):
            print("Redundant")
            return
        self.boards_hash[self.board.moving_side].add(board_config)
        row = list(board_config)
        best_eval = Dfs.get_best_eval(self.board, self.num_plies_ahead)
        # We don't want the model to learn evaluate checkmates, as it is much too complex to recognise.
        if abs(best_eval) == Dfs.checkmate_value:
            return
        row.append(best_eval)
        # num_rows, _ = self.training_data.shape
        # self.training_data.loc[num_rows] = row
        self.append_row_csv(self.filepaths[self.board.moving_side], row)