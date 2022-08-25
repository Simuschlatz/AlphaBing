import time

class Clock:
    @classmethod
    def init(cls, duration, player_one, player_two) -> None:
        cls.duration = [duration, duration]
        cls.player_one = player_one
        cls.player_two = player_two
        cls.c_time = time.perf_counter()
        cls.p_time = time.perf_counter()
        cls.r_min_tens = None
        cls.r_min_ones = None
        cls.r_sec_tens = None
        cls.r_sec_ones = None
        
    @classmethod
    def run(cls, moving_side):
        cls.c_time = time.perf_counter()
        dt = cls.c_time - cls.p_time
        cls.duration[moving_side] = max(0, cls.duration[moving_side] - dt)
        cls.p_time = cls.c_time

        cls.r_min_tens = [(round(cls.duration[i]) // 60) // 10 for i in range(2)]
        cls.r_min_ones = [(round(cls.duration[i]) // 60) % 10 for i in range(2)]
        cls.r_sec_tens = [(round(cls.duration[i]) % 60) // 10 for i in range(2)]
        cls.r_sec_ones = [round(cls.duration[i] % 60 % 10, 2) for i in range(2)]
        # print(*cls.duration)