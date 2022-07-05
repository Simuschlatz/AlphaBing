import time

class Game:
    def __init__(self, color_to_move, duration, player_one, player_two) -> None:
        self.color_to_move = color_to_move
        self.duration = [duration, duration]
        self.player_one = player_one
        self.player_two = player_two
        self.c_time = time.time()
        self.p_time = time.time()
        self.r_min_tens = None
        self.r_min_ones = None
        self.r_sec_tens = None
        self.r_sec_ones = None
        
    def switch_player_to_move(self):
        self.color_to_move = not self.color_to_move
        if self.color_to_move:
            print("red to move")
            return
        print("white to move")

    def run(self):
        self.c_time = time.time() # Or perf_counter()
        dt = self.c_time - self.p_time
        self.duration[self.color_to_move] = self.duration[self.color_to_move] - dt
        self.p_time = self.c_time
        self.r_min_tens = [(round(self.duration[i]) // 60) // 10 for i in range(2)]
        self.r_min_ones = [(round(self.duration[i]) // 60) % 10 for i in range(2)]
        self.r_sec_tens = [(round(self.duration[i]) % 60) // 10 for i in range(2)]
        self.r_sec_ones = [(round(self.duration[i]) % 60) % 10 for i in range(2)]
        # print(*self.duration)