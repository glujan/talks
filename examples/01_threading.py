import threading
import time


def some_job(name: str):
    time.sleep(1)  # our work done here
    print(name)


name_tmpl = 'Thread {}'
threads = []
MAX = 4

for i in range(MAX):
    name = name_tmpl.format(i)
    t = threading.Thread(target=some_job, args=(name, ))
    threads.append(t)

for t in threads:  # may be in a previous loop
    t.start()

for t in threads:
    t.join()
