import multiprocessing as mp
import random
import time
def change(i, v):
    return_val[i] = i
    time.sleep(1)
if __name__ == '__main__':
    # v = mp.Value('i', 0)
    manager = mp.Manager()
    return_val = manager.dict()
    processes = []
    for i in range(10):
        p = mp.Process(target=change, args=(return_val))
        processes.append(p)
    for p in processes:
        p.start()
        p.join()