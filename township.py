import os
import asyncio
import logging
import time
import random as ra
import websockets
import wave

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.WARNING, format=FORMAT)

PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/THE_MAYOR_OF_WHOVILLE"
MAYOR_PARAMS = wave._wave_params(1, 1, 8000, 128000, 'NONE', 'not compressed')


class Town:
    MAYOR_REQUEST = "We need to speak to the Mayor!"
    MAYOR_KEEPALIVE = "We still have them, done worry!"
    MAYOR_RETURN = "The mayor has done us a great service!"
    TOWNSHIP_HANDSAKE = "I'm just a township"
    TRANSMISSION_COMPLETE = "The mayor is in town!"
    CONFIRMED = "Mayor will be right there!"
    DENIED = "Sorry, the mayor is indisposed at the moment"
    WAIT_RANGE = 10
    WAIT_MINIMUM = 5
    MAYOR_RETURN_CHANCE = 0.3
    CHUNK = 1024
    def __init__(self, address):
        os.system("rm {}".format(FILE))
        self.uri = "ws://localhost:{}".format(address)
        self.name = ''

    async def initiate(self):
        async with websockets.connect(self.uri) as websocket:
            await self.identify(websocket)
            await self.township_activities(websocket)

    async def identify(self, websocket):
        await websocket.send(self.TOWNSHIP_HANDSAKE)
        self.name = await websocket.recv()
        self.path = FILE
        logging.warning("I have a name! My name is {}".format(self.name))

    async def township_activities(self, websocket):
        while True:
            if os.path.exists(self.path):
                await self.mayor_duties(websocket)
            else:
                await self.other_activities(websocket)
            await self.idle()

    async def idle(self):
        wait_time = (ra.random() * self.WAIT_RANGE) + self.WAIT_MINIMUM
        await asyncio.sleep(wait_time)

    async def mayor_duties(self, websocket):
        if ra.random() < self.MAYOR_RETURN_CHANCE:
            await self.return_mayor()
        else:
            await websocket.send(self.MAYOR_KEEPALIVE)
            logging.warning("Mayor is going about their important duties in {}".format(self.name))

    async def other_activities(self, websocket):
        activities = []
        activities.append(self.request_mayor())
        activities.append(self.send_gift(websocket))
        activities.append(self.recieve_aid(websocket))
        await asyncio.gather(*activities)

    async def request_mayor(self):
        async with websockets.connect(self.uri) as inner_websocket:
            await inner_websocket.send(self.MAYOR_REQUEST)
            response = await inner_websocket.recv()
            if response == self.CONFIRMED:
                logging.warning("Recieving mayor! Oh glorious day!")
                await self.receive_mayor(inner_websocket)
            elif response == self.DENIED:
                logging.warning("{} patiently waiting for the mayor to be available".format(self.name))

    async def receive_mayor(self, inner_websocket):
        with wave.open(self.path, 'wb') as fi:
            fi.setparams(MAYOR_PARAMS)
            while True:
                data = await inner_websocket.recv()
                if not data:
                    break
                fi.writeframes(data)

    async def return_mayor(self):
        async with websockets.connect(self.uri) as inner_websocket:
            await inner_websocket.send(self.MAYOR_RETURN)
            logging.info("Returning mayor! Farewell!")
            await self.send_mayor(inner_websocket)

    async def send_mayor(self, inner_websocket):
        with wave.open(self.path, 'rb') as fi:
            while True:
                byte_chunk = fi.readframes(self.CHUNK)
                await inner_websocket.send(byte_chunk)
                if not byte_chunk:
                    break
        os.system("rm {}".format(self.path))

    async def send_gift(self, websocket):
        logging.warning("{} has an excess of gold, sending some to CMA".format(self.name))
        await websocket.send(str(1000))
        await asyncio.sleep(5)

    async def recieve_aid(self, websocket):
        logging.info("{} needs help from CMA".format(self.name))
        gold = await websocket.recv()
        logging.warning("{} recieved {} gold pieces from CMA!".format(self.name, gold))

async def make_clients(num, address):
    towns = []
    for i in range(num):
        t = Town(address)
        towns.append(asyncio.ensure_future(t.initiate()))
    await asyncio.gather(*towns)

if __name__=="__main__":
    address = 8002
    num = 1
    asyncio.get_event_loop().run_until_complete(make_clients(num, address))
    asyncio.get_event_loop().run_forever()
