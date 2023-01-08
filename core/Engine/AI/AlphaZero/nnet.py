from .model import AlphaZeroModel
from . import TrainingConfig

import tensorflow as tf
from keras.utils import plot_model
from keras.optimizers import SGD
import keras.backend
import numpy as np
import os, datetime

class CNN(AlphaZeroModel):
    def __init__(self):
        self._build()
        self.opt = SGD(learning_rate=TrainingConfig.initial_lr, momentum=TrainingConfig.momentum)
        self.model.compile(optimizer=self.opt, loss=['categorical_crossentropy', 'mean_squared_error'])
    
    def predict(self, inp):
        return self.model.predict(self.bitboard_to_input(inp), verbose=False)

    @staticmethod
    def bitboard_to_input(bitboard, axis=0):
        """
        Converts array-like object with shape CNN.config.input_shape to tensor, 
        expands dimension along axis ```axis```, making it suitable as input to model
        :return: tensor of bitboard
        """
        return tf.expand_dims(bitboard, axis=axis)
    
    def process_training_data(self, training_data):
        """
        Puts the training data into the right shape
        :return: tuple containing features (bitboards) and labels (pi & v)
        """
        s, pi, v = zip(*training_data)
        v = np.asarray(v)
        pi = np.asarray(pi)
        x_train = np.asarray(s)
        y_train = [pi, v]
        return x_train, y_train

    def train(self, inputs):
        """
        Trains the neural network using examples from self-play with batch size
        ```TrainingConfig.batch_size``` and ```TrainingConfig.epochs``` epochs.

        input shape: [[s, pi, v], [s', pi', v'], ...]
        """
        x_train, y_train = self.process_training_data(inputs)
        self.model.fit(
            x=x_train, 
            y=y_train, 
            batch_size=TrainingConfig.batch_size, 
            epochs=TrainingConfig.epochs
            )

    def update_lr(self, iterations):
        for threshold, lr in TrainingConfig.iter_to_lr:
            if iterations >= threshold:
                keras.backend.set_value(self.opt.learning_rate, lr)

    def save_checkpoint(self, folder="./checkpoints", filename='checkpoint'):
        # change file type / extension
        if not filepath.endswith(".h5"):
            filename = filename.split(".")[0] + ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Making checkpoint directory {}...".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists!")
        print("Saving checkpoint...")
        self.model.save(filepath)

    def load_checkpoint(self, folder='./checkpoints', filename='checkpoint'):
        # change file type / extension
        if not filepath.endswith(".h5"):
            filename = filename.split(".")[0] + ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path '{}'".format(filepath))
        self.model.load_weights(filepath)

    def visualize(self, filepath="assets/imgs/ML"):
        filepath = os.path.join(filepath, "model" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")
        plot_model(self.model, filepath, show_shapes=True, show_layer_names=True)
