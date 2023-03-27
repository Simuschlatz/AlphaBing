import time
from multiprocessing import Process, Manager, Value


def foo(data, name=''):
    print(type(data), data.value, name)
    data.value += 1


if __name__ == "__main__":
    manager = Manager()
    x = manager.Value('i', 0)
    y = Value('i', 0)

    for i in range(5):
        Process(target=foo, args=(x, 'x')).start()
        Process(target=foo, args=(y, 'y')).start()

    print('Before waiting: ')
    print('x = {0}'.format(x.value))
    print('y = {0}'.format(y.value))

    time.sleep(5.0)
    print('After waiting: ')
    print('x = {0}'.format(x.value))
    print('y = {0}'.format(y.value))