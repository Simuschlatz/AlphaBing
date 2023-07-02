from core.engine import PrecomputingMoves
import os
import tensorflow as tf
import keras
from datetime import datetime
from ..config import BaseConfig

class ModelConfig(BaseConfig):
    input_depth = 14
    input_shape = (2, 7, 90)
    input_kernel_size = 5
    kernel_size = 3
    num_filters = 256
    num_res_layers = 7
    policy_output_size = PrecomputingMoves.action_space
    l2_reg_const = 1e-4
    value_fc_layer_size = 256
    distributed = False
    

class PlayConfig(BaseConfig):
    simulations_per_move = 25
    cpuct = 1.5
    noise_eps = .15
    dirichlet_alpha = .2
    resign_threshold = -.98
    min_resign_turn = 40
    enable_resign_rate = 0.5

    tau_decay_rate = .95
    tau_decay_threshold = 30 # threshold of plies when tau starts to decay
    self_play_eps = 7
    training_iterations = 10
    steps_per_save = 2
    max_training_data = 5000 # Max number of training examples

    examples_filename = "examples"


class TensorboardBaseConfig:
    tensorboard_logdir = os.path.join(BaseConfig.checkpoint_location, "logs/scalars", datetime.now().strftime("%Y%m%d-%H%M%S"))
    tensorboard_callback = keras.callbacks.TensorBoard(log_dir=tensorboard_logdir)

class TrainingConfig(BaseConfig, TensorboardBaseConfig):
    initial_lr = .01
    momentum = .9
    iter_to_lr = [
        (150000, 3e-3),
        (400000, 1e-4)
        ]
    epochs = 1
    batch_size = 64

class EvaluationConfig(BaseConfig, TensorboardBaseConfig):
    step_size = 2 # Number of iterations between each evaluation session
    episodes = BaseConfig.max_processes
    elo_rating_filename = "elo"
    win_rate_filename = "win_rate"
    baseline_rating = 200 # Elo of random agent
    eval_writer = tf.summary.create_file_writer(TensorboardBaseConfig.tensorboard_logdir + "/eval")
    eval_writer.set_as_default()