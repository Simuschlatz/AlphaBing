from multiprocessing import cpu_count
from core.engine import PrecomputingMoves

class BaseConfig:
    checkpoint_location = "core/Engine/AI/AlphaZero/checkpoints"
    new_model_checkpoint = "checkpoint_new.h5"
    old_model_checkpoint = "checkpoint_old.h5"
    max_processes = cpu_count()

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

    tau_decay_rate = .9
    tau_decay_threshold = 30 # threshold of plies when tau starts to decay
    self_play_eps = 7
    training_iterations = 10
    steps_per_save = 2
    max_training_data = 5000 # Max number of training examples

    examples_filename = "examples"


class TrainingConfig(BaseConfig):
    initial_lr = .01
    momentum = .9
    iter_to_lr = [
        (150000, 3e-3),
        (400000, 1e-4)
        ]
    epochs = 40
    batch_size = 64

class EvaluationConfig(BaseConfig):
    episodes = cpu_count()
    elo_rating_filename = "elo"
    win_rate_filename = "win_rate"
    baseline_rating = 200 # Elo of random agent