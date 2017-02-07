from functools import partial
from multiprocessing.dummy import Pool
from multiprocessing import Lock
import time


def some_job(line: str, lock: Lock=None):
    time.sleep(1)  # no worries about resources here

    with open('/tmp/locked_file', 'a+') as f, lock:
        print(line, file=f)

    time.sleep(1)  # again, no worries here


name_tmpl = 'Thread {}'
threads = []
MAX = 8

lock = Lock()
locked_job = partial(some_job, lock=lock)

with Pool(MAX) as pool:
    lines = (name_tmpl.format(i) for i in range(MAX))
    pool.map(locked_job, lines)
