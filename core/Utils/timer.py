from time import perf_counter

def time_benchmark(func):
    def wrapper(*args, **kwargs):
        t0 = perf_counter()
        res = func(*args, **kwargs)
        print(perf_counter() - t0)
        return res
    return wrapper