from . import CNN, MCTS, PlayConfig
from core.Engine import Board, LegalMoveGenerator

import numpy as np
from random import shuffle

import multiprocessing as mp
from copy import deepcopy


class SelfPlay:
    def __init__(self, nnet: CNN, board: Board) -> None:
        self.nnet = nnet
        self.board = board
        self.mcts = MCTS(nnet)
        self.training_data = []
    
    def execute_episode(self, training_examples=None, board: Board=None, mcts: MCTS=None):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data. when a terminal state is reached, each training example's
        value v is the outcome z of that game from the sample's side's perspective.
        
        :param training_examples, board, mcts: only for multiprocessing. If not specified, returns
        a list of training examples. If specified, they extend training_examples. Form: (s, pi, v) 
        where s is the state represented
        
        as set of bitboards, pi is the probability distribution returned by MCTS, for v see above.
        :param training_examples: used for multiprocessing, a ```mp.Manager().list()``` object, 
        shared memory containing the training examples from episode's self-play iteration
        """
        board = board or self.board
        mcts = mcts or self.mcts
        training_data = []
        plies, tau = 0, 1
        moves = LegalMoveGenerator.load_moves(board)
        while True:
            bb = list(board.piecelist_to_bitboard(adjust_perspective=True))
            # if plies > PlayConfig.tau_decay_threshold:
            #     tau = round(PlayConfig.tau_decay_rate ** (plies - PlayConfig.tau_decay_threshold), 2)
            tau = plies < PlayConfig.tau_decay_threshold
            pi = mcts.get_probability_distribution(board, bitboards=bb, moves=moves, tau=tau)
            side = board.moving_side

            training_data.append([bb, pi, side])
            move = MCTS.best_action_from_pi(board, pi)

            board.make_move(move, search_state=False)
            plies += 1
            moves = LegalMoveGenerator.load_moves(board)
            status = board.get_terminal_status(len(moves))
            if status == -1: continue
            # print("GAME ENDED")
            # negative outcome for every example where the side was current (mated) moving side
            if training_examples is None:
                return [[ex[0], ex[1], 1 * (1 - 2 * ex[2] == board.moving_side)] for ex in training_data]

            training_examples.extend([[ex[0], ex[1], 1 * (1 - 2 * ex[2] == board.moving_side)] for ex in training_data])
            return

    @staticmethod
    def batch(iterable, batch_size):
        for ndx in range(0, len(iterable), batch_size):
            yield iterable[ndx:min(len(iterable), ndx+batch_size)]

    def multiprocess_train(self):
        """
        Performs self-play for ```PlayConfig.training_iterations``` iterations of `
        ``PlayConfig.self_play_eps``` episodes each. Every episode is executed in a separate process 
        allowing them to run in parallel. The maximum length of training data is the examples from the 
        last ```PlayConfig.max_training_data_length``` iterations. After each iteration, the neural 
        network is retrained.
        """
        for i in range(1, PlayConfig.training_iterations + 1):
            print(f"starting self-play iteration no. {i}")
            iteration_data = mp.Manager().list() # Shared list
            jobs = [mp.Process(target=self.execute_episode(iteration_data, deepcopy(self.board), deepcopy(self.mcts))) for _ in range(PlayConfig.self_play_eps)]
            for processes in self.batch(jobs, PlayConfig.max_processes):
                print("------starting process-------")
                for p in processes: p.start()
                for p in processes: p.join()

            self.training_data.append(iteration_data)

            if len(self.training_data) > PlayConfig.max_training_data_length:
                self.training_data.pop(0)

            train_examples = [example for iteration_data in self.training_data for example in iteration_data]  
 
            shuffle(train_examples)

            print(np.asarray(train_examples, dtype=object).shape)
            self.nnet.train(train_examples)

    def train(self):
        """
        Performs self-play for ```PlayConfig.training_iterations``` iterations of 
        ```PlayConfig.self_play_eps``` episodes  each. The maximum length of training data is the 
        examples from the last ```PlayConfig.max_training_data_length```  iterations. After each 
        iteration, the neural  network is retrained.
        """
        for i in range(1, PlayConfig.training_iterations + 1):
            print(f"starting self-play iteration no. {i}")
            iteration_training_data = []


            for _ in range(PlayConfig.self_play_eps):
                self.mcts = MCTS(self.nnet)
                eps_training_data = self.execute_episode()
                iteration_training_data.extend(eps_training_data)
            

            self.training_data.append(iteration_training_data)
            if len(self.training_data) > PlayConfig.max_training_data_length:
                self.training_data.pop(0)

            # if not i % PlayConfig.steps_per_save:
            #     self.save_training_data()
            # collapse 3D list to 2d list
            train_examples = [example for iteration_data in self.training_data for example in iteration_data]  
 
            shuffle(train_examples)

            # print(np.asarray(train_examples, dtype=object).shape)
            self.nnet.train(train_examples)

            
    def load_training_data(self, folder, filename):
        pass

    def save_training_data(self, folder, filename):
        pass
            
            


    