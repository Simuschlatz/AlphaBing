from .config import ModelConfig

import tensorflow as tf

from keras.models import Model
from keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, Activation, Add
from keras.regularizers import l2


class Model:
    
    def _conv_layer(self, input, num_filters: int, kernel_size: int, name:str=None, prefix: str=""):
        """
        builds a convolutional layer with given parameters. Applies BatchNorm and ReLu Activation.
        :param index: (0, ∞]
        """
        name = name or prefix + "_conv1"

        x = Conv2D(
            filters=num_filters, 
            kernel_size=kernel_size, 
            padding="same",
            data_format="channels_first", 
            use_bias=False, 
            kernel_regularizer=l2(ModelConfig.l2_reg_const), 
            name=name)(input)
        x = BatchNormalization(axis=1, name=name+"_bn")(x)
        x = Activation("relu", name=name+"_relu")(x)

        return x

    def _residual_block(self, input, index: int):
        name = "res" + str(index)

        x = self._conv_layer(input, ModelConfig.num_filters, ModelConfig.kernel_size, prefix=name)

        x = Conv2D(
            filters=ModelConfig.num_filters, 
            kernel_size=ModelConfig.kernel_size, 
            padding="same",
            data_format="channels_first", 
            use_bias=False, 
            kernel_regularizer=l2(ModelConfig.l2_reg_const), 
            name=name+"_conv2")(x)

        x = BatchNormalization(axis=1, name="res"+str(index)+"_bn")(x)
        x = Add(name=name+"_add")([input, x])
        x = Activation("relu", name=name+"_relu")(x)
        return x

    def _value_head(self, input):
        """
        :return: the value head of the AlphaZero model
        The value head consists of one convolutional filter, BatchNorm, ReLu, 
        two fc layers with ReLu and tanh activation and outputs a scalar value in number range [-1, 1]
        """
        x = self._conv_layer(input, 1, 1, name="value_conv")
        x = Flatten(name="value_flatten")(x)
        x = Dense(ModelConfig.value_fc_layer_size, 
            kernel_regularizer=l2(ModelConfig.l2_reg_const), 
            activation="relu", 
            name="value_dense")(x)
        x = Dense(1, 
            kernel_regularizer=l2(ModelConfig.l2_reg_const), 
            activation="tanh", 
            name="value_out")(x)
        return x
    
    def _policy_head(self, input):
        x = self._conv_layer(input, 4, 1, name="policy_conv")
        x = Flatten(name="policy_flatten")(x)
        x = Dense(ModelConfig.policy_output_size, 
            kernel_regularizer=l2(ModelConfig.l2_reg_const), 
            activation="softmax", 
            name="policy_out")(x)
        return x

    def _build(self) -> Model:
        """
        builds the AlphaZero model
        """
        in_x = Input(shape=ModelConfig.input_shape, name="input_layer", dtype=tf.float16)
        x = self._conv_layer(in_x, ModelConfig.num_filters, ModelConfig.input_kernel_size, name="input_conv")
        # Residual Layers
        for i in range(ModelConfig.num_res_layers):
            x = self._residual_block(x, i+1)
        
        value_head = self._value_head(x)
        policy_head = self._policy_head(x)

        self.model = Model(in_x, [policy_head, value_head], name="Model")
