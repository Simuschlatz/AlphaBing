from .model import ModelArch
from . import TrainingConfig, ModelConfig

import tensorflow as tf
from keras.utils import plot_model
from keras.models import load_model
from keras.optimizers import SGD
import keras.backend

import numpy as np
import os, datetime

from logging import getLogger
logger = getLogger(__name__)

class CNN(ModelArch):
    def __init__(self):
        self._build()
        self.opt = SGD(learning_rate=TrainingConfig.initial_lr, momentum=TrainingConfig.momentum)
        self.model.compile(optimizer=self.opt, 
                        loss=['categorical_crossentropy', 'mean_squared_error'],
                        metrics=['accuracy']
                        )
    
    def predict(self, inp):
        return self.model.predict(self.bitboard_to_input(inp), verbose=False)

    @staticmethod
    def bitboard_to_input(bitboards, axis=0):
        """
        Converts array-like object with shape ``CNN.config.input_shape`` to tensor, 
        expands dimension along axis ``axis``, making it suitable as input to model
        :return: tensor of bitboard
        """
        return tf.expand_dims(bitboards, axis=axis)
    
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

    def train(self, inputs: list):
        """
        Trains the neural network using examples from self-play with batch size
        ``TrainingConfig.batch_size`` and ``TrainingConfig.epochs`` epochs.

        input shape: [[s, pi, v], [s', pi', v'], ...]
        """
        x_train, y_train = self.process_training_data(inputs)
        
        self.model.fit(
            x=x_train, 
            y=y_train, 
            batch_size=TrainingConfig.batch_size, 
            epochs=TrainingConfig.epochs,
            callbacks=[TrainingConfig.tensorboard_callback],
            )

    def update_lr(self, iterations: int):
        for threshold, lr in TrainingConfig.iter_to_lr:
            if iterations >= threshold:
                keras.backend.set_value(self.opt.learning_rate, lr)#

    @staticmethod
    def update_checkpoint_versions(new_network, 
                        folder=ModelConfig.checkpoint_location,
                        old_cp=ModelConfig.old_model_checkpoint, 
                        new_cp=ModelConfig.new_model_checkpoint):
        """
        :param new_network: a CNN object trained with data from self play gathered with the current network
        updates the filename of previous weights and saves the new model's weights as the current ones
        """
        new_checkpoint, old_checkpoint = os.path.join(folder, new_cp), os.path.join(folder, old_cp)
        if not os.path.exists(new_checkpoint):
            logger.warning("404 no model version checkpoint found. Doing a workaround...")
        else:
            logger.info("Updating model versions...")
            os.rename(new_checkpoint, old_checkpoint)
            logger.info("Done!")
        new_network.save_checkpoint()

    def save_checkpoint(self, folder=ModelConfig.checkpoint_location, filename=ModelConfig.new_model_checkpoint):
        """
        Saves checkpoint of current model
        """
        # change file type / extension
        if not filename.endswith(".h5"):
            filename = filename.split(".")
            filename = ".".join(filename) + ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            logger.info(f"Making checkpoint directory {folder}...")
            os.mkdir(folder)
        else:
            logger.info("Checkpoint Directory exists!")
        logger.info("Saving checkpoint...")
        self.model.save_weights(filepath)

    def load_checkpoint(self, folder=ModelConfig.checkpoint_location, filename=ModelConfig.new_model_checkpoint, save_model_if_no_file=True):
        """
        Loads a checkpoint file and updates weights of current model
        """
        # change file type / extension
        if not filename.endswith(".h5"):
            filename = filename.split(".")
            filename = ".".join(filename) + ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            if save_model_if_no_file:
                logger.warning("404 target checkpoint file not found. Doing a workaround...")
                self.save_checkpoint()
                return
            raise FileNotFoundError(f"No model in path '{filepath}")
        logger.info("Loading checkpoint...")
        self.model.load_weights(filepath)
        logger.info("Done loading!")

    @staticmethod
    def load_nnet(current_model=True):
        """
        :return: The model from the checkpoint file specified in 
        """
        nnet_filename = ModelConfig.new_model_checkpoint if current_model else ModelConfig.old_model_checkpoint
        nnet = CNN()
        nnet.load_checkpoint(filename=nnet_filename)
        return nnet

    def visualize(self, filepath="assets/imgs/ML"):
        filepath = os.path.join(filepath, "model" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")
        plot_model(self.model, filepath, show_shapes=True, show_layer_names=True)
        