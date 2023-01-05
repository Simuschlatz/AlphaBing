from .model import AlphaZeroModel

import tensorflow as tf
from keras.utils import plot_model

import os, datetime

class CNN(AlphaZeroModel):
    def __init__(self):
        super().__init__()
        
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
        filename = filename.split(".")[0] + ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path '{}'".format(filepath))
        self.model.load_weights(filepath)

    def visualize(self, filepath="assets/imgs/ML"):
        filepath = os.path.join(filepath, "model" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")
        plot_model(self.model, filepath, show_shapes=True, show_layer_names=True)

    def predict(self, inp):
        return self.model.predict(self.bitboard_to_input(inp))

    @staticmethod
    def bitboard_to_input(bitboard):
        """
        converts array-like object with shape CNN.config.input_shape to tensor, 
        expands dimension along axis 0, making it suitable as input to model
        :return: tensor of bitboard
        """
        return tf.expand_dims(bitboard, axis=0)
    
