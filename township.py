import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

class Client:
    def __init__(self, address):
        self.uri = "ws://localhost:{}".format(address)
        self.name = ''

    async def initiate(self):
        async with websockets.connect(self.uri) as websocket:
            self.name = await websocket.recv()
            logging.info("I have a name! My name is {}".format(self.name))
            await self.choose_my_function(websocket)

    async def print_message_angrily(self, websocket):
        while True:
            await asyncio.sleep(ra.random() * 3)
            message = await websocket.recv()
            logging.info("{} says: Fuckin {}!".format(self.name, message))

    async def print_message_happily(self, websocket):
        while True:
            await asyncio.sleep(ra.random() * 3)
            message = await websocket.recv()
            logging.info("{} says: Love those {}!".format(self.name, message))

    async def send_message_back(self, websocket):
        while True:
            await asyncio.sleep(ra.random() * 3)
            await websocket.send("hello from {} servi!".format(self.name))

    async def choose_my_function(self, websocket):
        tasks = []
        tasks.append(self.print_message_angrily)
        tasks.append(self.print_message_happily)
        tasks.append(self.send_message_back)
        choice = ra.randint(0, len(tasks) - 1)
        await tasks[choice](websocket)

if __name__=="__main__":
    address = 8002
    c = Client(address)
    asyncio.get_event_loop().run_until_complete(c.initiate())
    asyncio.get_event_loop().run_forever()
