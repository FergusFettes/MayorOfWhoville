import os
import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/THE_MAYOR_OF_WHOVILLE_IN_"


class Town:
    MAYOR_REQUEST = "We need to speak to the Mayor!"
    TOWNSHIP_HANDSAKE = "I'm just a township"
    TRANSMISSION_COMPLETE = "The mayor is in town!"
    CONFIRMED = "Mayor will be right there!"
    DENIED = "Sorry, the mayor is indisposed at the moment"
    WAIT_RANGE = 10
    WAIT_MINIMUM = 5
    def __init__(self, address):
        self.uri = "ws://localhost:{}".format(address)
        self.name = ''

    async def initiate(self):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(self.TOWNSHIP_HANDSAKE)
            self.name = await websocket.recv()
            self.path = FILE + self.name
            logging.info("I have a name! My name is {}".format(self.name))
            while True:
                if os.path.exists(self.path):
                    logging.info("Mayor is going about their important duties in {}".format(self.name))
                else:
                    await self.request_mayor()
                wait_time = (ra.random() * self.WAIT_RANGE) + self.WAIT_MINIMUM
                await asyncio.sleep(wait_time)

    async def request_mayor(self):
        async with websockets.connect(self.uri) as inner_websocket:
            await inner_websocket.send(self.MAYOR_REQUEST)
            response = await inner_websocket.recv()
            if response == self.CONFIRMED:
                logging.info("Recieving mayor! Oh glorious day!")
                await self.receive_mayor(inner_websocket)
            elif response == self.DENIED:
                logging.info("{} patiently waiting for the mayor to be available".format(self.name))

    async def receive_mayor(self, inner_websocket):
        with open(self.path, 'wb') as fi:
            while True:
                data = await inner_websocket.recv()
                if not data:
                    break
                fi.write(data)

async def make_clients(num, address):
    towns = []
    for i in range(num):
        t = Town(address)
        towns.append(asyncio.ensure_future(t.initiate()))
    await asyncio.gather(*towns)

if __name__=="__main__":
    address = 8002
    num = 3
    asyncio.get_event_loop().run_until_complete(make_clients(num, address))
    asyncio.get_event_loop().run_forever()
