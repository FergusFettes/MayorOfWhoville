import asyncio
import logging
import time

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

# When this one is included, it blocks for two seconds
async def say_hello_time():
    time.sleep(2)
    logging.info("Simple (time) Hello!")

async def say_hello():
    await asyncio.sleep(2)
    logging.info("Simple Hello!")


async def say_hello_after_time(time):
    await asyncio.sleep(time)
    logging.info("Hello!")

async def many_hellos():
    tasks = []
    tasks.append(say_hello())
    for i in range(5):
        tasks.append(say_hello_after_time(i))
    await asyncio.gather(*tasks)

if __name__=="__main__":
    asyncio.get_event_loop().run_until_complete(many_hellos())
