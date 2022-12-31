from core.Engine.AI.AlphaZero.config import ModelConfifg

import tensorflow as tf
from keras.models import Sequential, load_model, Model
from keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, Activation, LeakyReLU, Add
from keras.optimizers import SGD
from keras.regularizers import l2

class Model:
    def __init__(self, config: ModelConfifg):
        self.config = config
        self.model = None

    def _conv_layer(self, input, num_filters, kernel_size, name=None):
        """
        builds a convolutional layer with given parameters. Applies BatchNorm and ReLu Activation.
        :param index: (0, ∞]
        """
        if name is None:
            name = "conv_layer"

        x = Conv2D(
            filters=num_filters, 
            kernel_size=kernel_size, 
            padding="same",
            data_format="channels_first", 
            use_bias=False, 
            kernel_regularizer=l2(self.config.l2_reg_const), 
            name=name)(input)
        x = BatchNormalization(axis=1, name=name+"_BN")(x)
        x = Activation("relu", name=name+"_ReLu")(x)

        return x

    def _residual_block(self, input, index):
        name = "Res" + str(index)

        x = self._conv_layer(input, self.config.num_filters, self.config.kernel_size)

        x = Conv2D(
            filters=self.config.num_filters, 
            kernel_size=self.config.kernel_size, 
            padding="same",
            data_format="channels_first", 
            use_bias=False, 
            kernel_regularizer=l2(self.config.l2_reg_const), 
            name=name)(x)

        x = BatchNormalization(axis=1, name="res"+str(index)+"_batchnorm2")(x)
        x = Add(name=name+"_add")([input, x])
        x = Activation("relu", name=name+"_relu2")(x)
        return x

    def _value_head(self, input):
        """
        :return: the value head of the AlphaZero model 
        The value head consists of one convolutional filter, BatchNorm, ReLu, 
        two fc layers with ReLu and tanh activation and outputs a scalar value in number range [-1, 1]
        """
        x = self._conv_layer(input, 1, 1, name="value_conv")
        x = Flatten(name="value_flatten")(x)
        x = Dense(self.config.value_fc_layer_size, 
            kernel_regularizer=l2(self.config.l2_reg_const), 
            activation="relu", 
            name="value_dense")(x)
        x = Dense(1, 
            kernel_regularizer=l2(self.config.l2_reg_const), 
            activation="tanh", 
            name="value_head")(x)
        return x
    
    def _policy_head(self, input):
        x = self._conv_layer(input, 4, 1, name="policy_conv")
        x = Flatten(name="policy_flatten")(x)
        x = Dense(self.config.policy_output_size, 
            kernel_regularizer=l2(self.config.l2_reg_const), 
            activation="softmax", 
            name="policy_head")(x)
        return x

    def build(self):
        in_x = Input(self.config.input_shape, name="input_layer")
        x = self._conv_layer(in_x, self.config.num_filters, self.config.input_kernel_size, name="input_conv")
        # Residual Layers
        for i in range(self.config.num_res_layers):
            x = self._residual_block(x, i+1)
        
        value_head = self._value_head(x)
        policy_head = self._policy_head(x)

        self.model = Model(in_x, [policy_head, value_head], name="alphazero_model")
        
        
        
