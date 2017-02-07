from concurrent.futures import ThreadPoolExecutor
import time


def some_job(name: str):
    time.sleep(1)  # our work done here
    print(name)


name_tmpl = 'Thread {}'
threads = []
MAX = 4

with ThreadPoolExecutor(max_workers=MAX) as executor:
    names = (name_tmpl.format(i) for i in range(MAX))
    executor.map(some_job, names)
    # or: executor.submit(some_job, 'Some name')
