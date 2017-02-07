from multiprocessing.dummy import Pool
import time


def some_job(name: str):
    time.sleep(1)  # our work done here
    print(name)


name_tmpl = 'Thread {}'
threads = []
MAX = 4

with Pool(MAX) as pool:
    names = (name_tmpl.format(i) for i in range(MAX))
    pool.map(some_job, names)
