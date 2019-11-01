import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

class Client:

    async def print_message_angrily(self,address):
        uri = "ws://localhost:{}".format(address)
        async with websockets.connect(uri) as websocket:
            name = await websocket.recv()
            logging.info("I have a name! My name is {}".format(name))
            while True:
                await asyncio.sleep(ra.random() * 3)
                message = await websocket.recv()
                logging.info("{} says: Fuckin {}!".format(name, message))

    async def print_message_happily(self,address):
        uri = "ws://localhost:{}".format(address)
        async with websockets.connect(uri) as websocket:
            name = await websocket.recv()
            logging.info("I have a name! My name is {}".format(name))
            while True:
                await asyncio.sleep(ra.random() * 3)
                message = await websocket.recv()
                logging.info("{} says: Love those {}!".format(name, message))

    async def send_message_back(self,address):
        uri = "ws://localhost:{}".format(address)
        async with websockets.connect(uri) as websocket:
            name = await websocket.recv()
            logging.info("I have a name! My name is {}".format(name))
            while True:
                await asyncio.sleep(ra.random() * 3)
                await websocket.send("hello from {} servi!".format(name))


    async def server_and_clients(self,address):
        tasks = []
        tasks.append(print_message_angrily(address))
        tasks.append(print_message_happily(address))
        tasks.append(send_message_back(address))
        await asyncio.gather(*tasks)

if __name__=="__main__":
    address = 8002
    asyncio.get_event_loop().run_until_complete(server_and_clients(address))
    asyncio.get_event_loop().run_forever()
