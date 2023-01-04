from time import perf_counter

def time_benchmark(func):
    def wrapper(*args, **kwargs):
        t0 = perf_counter()
        res = func(*args, **kwargs)
        name = func.__name__
        print(f"{name} took {perf_counter() - t0} seconds")
        return res
    return wrapper