from time import perf_counter
from logging import getLogger
logger = getLogger(__name__)
import os
from pickle import Pickler, Unpickler

def time_benchmark(func):
    def wrapper(*args, **kwargs):
        t0 = perf_counter()
        res = func(*args, **kwargs)
        name = func.__name__
        logger.info(f"{name} took {perf_counter() - t0} seconds")
        return res
    return wrapper

def save_time_list(func):
    def wrapper(l, *args, **kwargs):
        t0 = perf_counter()
        res = func(*args, **kwargs)
        name = func.__name__
        dt = perf_counter() - t0
        logger.info(f"{name} took {dt} seconds")
        l.append(dt)
        return res
    return wrapper

def save_time_benchmark(func):
    def wrapper(*args, funcname=None, filename="visualizations/data", divident: int=1, **kwargs):
        t0 = perf_counter()
        res = func(*args, **kwargs)
        dt = perf_counter() - t0
        name = funcname or func.__name__
        msg = f"{name} took {dt} seconds"
        logger.info(msg)
        dt = dt / divident
        if not os.path.exists(filename):
            data = {name: [dt]}
        else:
            with open(filename, "rb") as f:
                data = Unpickler(f).load()
                data[name] = data.get(name, []) + [dt]
        with open(filename, 'wb+') as f:
            Pickler(f).dump(data)
        return res
    return wrapper