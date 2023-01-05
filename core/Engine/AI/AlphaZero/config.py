from multiprocessing import cpu_count
from core.Engine import PrecomputingMoves

class ModelConfifg:
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

class PlayConfig:
    max_processes = cpu_count()
    simulations_per_move = 4
    cpuct = 1.5
    noise_eps = 0.15
    dirichlet_alpha = 0.2
    resign_threshold = -0.98
    min_resign_turn = 40
    enable_resign_rate = 0.5

    tau_decay_rate = 0.95
    episodes = 1
    selfplay_iterations = 1
    steps_per_save = 2
    max_training_data_length = 100
