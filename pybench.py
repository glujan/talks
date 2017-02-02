#! /usr/bin/env python

import argparse
import time

from functools import wraps
from threading import Thread
from multiprocessing import Pool


def print_time(f):
    @wraps(f)
    def inner(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        delta = time.time() - start
        print(f'{f.__name__:>13}: {delta:.08f}')
        return result

    return inner


@print_time
def single_thread(func, nb_repeat):
    for _ in range(nb_repeat):
        func()


@print_time
def process_pool(func, nb_repeat):
    pool = Pool(processes=nb_repeat)
    pool.map(func, [None for _ in range(nb_repeat)])


@print_time
def threads(func, nb_repeat):
    threads = [Thread(target=func) for _ in range(nb_repeat)]
    [x.start() for x in threads]
    [x.join() for x in threads]


def io_bound(*args):
    time.sleep(0.5)


def cpu_bound(*args):
    a = []
    for x in range(999999):
        a.append(x)


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Benchmark concurrency and parallelism in Python.')

    parser.add_argument(
        '-t', '--type', dest='func_types', nargs='+', required=True,
        choices={'io', 'cpu'}, help='Which benchmark to run')

    parser.add_argument(
        '-r', '--repeat', dest='nb_repeat', default=15, type=int,
        help='Number of iterations, processes and threads to run ')

    return parser.parse_args()


def _run():
    args = _parse_args()

    funcs = {
        'io': io_bound,
        'cpu': cpu_bound,
    }

    for func_type in args.func_types:
        print(f'\n{func_type} benchmark: ')

        func = funcs[func_type]
        single_thread(func, args.nb_repeat)
        process_pool(func, args.nb_repeat)
        threads(func, args.nb_repeat)


if __name__ == '__main__':
    _run()
