# Parallelizing using Pool.map()
import multiprocessing as mp
import numpy as np
import time

# Prepare data
np.random.RandomState(100)
arr = np.random.randint(0, 10, size=[200000, 50])
data = arr.tolist()
data[:5]

# Redefine, with only 1 mandatory argument.
def howmany_within_range(row, minimum=4, maximum=8):
    count = 0
    for n in row:
        if minimum <= n <= maximum:
            count = count + 1
    return count

if __name__ == '__main__':

    t = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(howmany_within_range, data)
    pool.close()

    print(results[:10], time.time()-t)

    t = time.time()
    results = []
    for row in data:
        results.append(howmany_within_range(row, minimum=4, maximum=8))

    print(results[:10], time.time()-t)