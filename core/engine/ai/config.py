from multiprocessing import cpu_count

class BaseConfig:
    checkpoint_location = "core/Engine/ai/selfplay_rl/checkpoints"
    new_model_checkpoint = "checkpoint_new.h5"
    old_model_checkpoint = "checkpoint_old.h5"
    max_processes = cpu_count()
