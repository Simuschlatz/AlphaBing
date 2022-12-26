from multiprocessing import cpu_count

class ModelConfifg:
    input_shape = (14, 10, 9)
    input_filter_size = 5
    filter_size = 3
    num_filters = 256
    num_hidden_layers = 7
    l2_regularization = 1e-4
    value_fc_size = 256
    distributed = False
    input_depth = 14

class PlayConfig:
    max_processes = cpu_count()
    search_threads = 30
    vram_frac = 1.0
    simulation_num_per_move = 800
    logging_thinking = False
    c_puct = 1.5
    noise_eps = 0.15
    dirichlet_alpha = 0.2
    tau_decay_rate = 0.9
    virtual_loss = 3
    resign_threshold = -0.98
    min_resign_turn = 40
    enable_resign_rate = 0.5
    max_game_length = 100
    share_mtcs_info_in_self_play = False
    reset_mtcs_info_per_game = 5
