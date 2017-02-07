import asyncio
from contextlib import closing


async def some_job(name: str):
    await asyncio.sleep(1)
    print(name)


name_tmpl = 'Coro {}'
coroutines = []
MAX = 4

loop = asyncio.get_event_loop()
names = (name_tmpl.format(i) for i in range(MAX))
coros = (some_job(n) for n in names)

with closing(loop) as loop:
    loop.run_until_complete(asyncio.gather(*coros))
