from core.Engine.AI.AlphaZero.agent.config import ModelConfifg

from keras.models import Sequential, load_model, Model
from keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, Activation, LeakyReLU, Add
from keras.optimizers import SGD
from keras.regularizers import l2

class Model:
    def __init__(self, config: ModelConfifg):
        self.config = config
        self.model = None
    
    def _residual_block(self, input, index):
        in_x = x
        name = "res" + str(index)
        x = Conv2D(
            filters=self.config.num_filters, 
            kernel_size=self.config.filter_size, 
            padding="same",
            data_format="channels_first", 
            use_bias=False, 
            kernel_regularizer=l2(self.config.l2_reg), 
            name=name)(x)

        x = BatchNormalization(axis=1, name="res"+str(index)+"_batchnorm2")(x)
        x = Add(name=name+"_add")([in_x, x])
        x = Activation("relu", name=name+"_relu2")(x)
        return x
