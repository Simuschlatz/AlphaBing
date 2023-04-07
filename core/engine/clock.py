import time

class Clock:
    @classmethod
    def init(cls, duration_s: int) -> None:
        cls.duration = [duration_s, duration_s]
        cls.p_time = time.perf_counter()
        # Formatted time strings
        cls.ftime = [cls.get_ftime_string(duration_s) for _ in range(2)]

    @staticmethod
    def get_ftime_string(secs: int):
        total_secs = round(secs)
        mins, seconds = divmod(total_secs, 60)

        min_tens, min_ones = divmod(mins, 10)
        
        sec_tens, sec_ones = divmod(seconds, 10)

        ftime = f"{min_tens}{min_ones}:{sec_tens}{sec_ones}"
        return ftime

    @classmethod
    def update_ftime(cls, moving_side):
        cls.ftime[moving_side] = cls.get_ftime_string(cls.duration[moving_side])

    @classmethod
    def run(cls, moving_side):
        c_time = time.perf_counter()
        dt = c_time - cls.p_time
        cls.p_time = c_time
        cls.duration[moving_side] = max(0, cls.duration[moving_side] - dt)
        cls.update_ftime(moving_side)
        # print(*cls.duration)