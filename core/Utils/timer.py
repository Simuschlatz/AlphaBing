"""
Copyright (C) 2022-2023 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
from time import perf_counter
import logging

logger = logging.getLogger(__name__)

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
    def wrapper(*args, filename="core/visualizations/data", **kwargs):
        t0 = perf_counter()
        res = func(*args, **kwargs)
        name = func.__name__
        msg = f"{name} took {perf_counter() - t0} seconds"
        logger.info(msg)
        with open(filename, 'w') as f:
            f.write(msg)
        return res
    return wrapper