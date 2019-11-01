import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

class Town:
    MAYOR_REQUEST = "We need to speak to the Mayor!"
    TRANSMISSION_COMPLETE = "The mayor is in town!"
    TOWNSHIP_HANDSAKE = "I'm just a township"
    def __init__(self, address):
        self.uri = "ws://localhost:{}".format(address)
        self.name = ''
        self.tranmission_ongoing = False

    async def initiate(self):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(self.TOWNSHIP_HANDSAKE)
            self.name = await websocket.recv()
            logging.info("I have a name! My name is {}".format(self.name))
            func = self.choose_my_function()
            await func(websocket)

    async def process_transmission(self, websocket):
        self.receive_mayor()
        message = await websocket.recv()
        logging.info("Processor got a message: {}".format(message))
        if message == TRANSMISSION_COMPLETE:
            self.tranmission_ongoing = False

    async def receive_mayor(self):
        async with websockets.connect(self.uri) as inner_websocket:
            await inner_websocket.send(MAYOR_REQUEST)
            await inner_websocket.send(self.name)
            self.tranmission_ongoing = True
            path = os.path.dirname(os.path.realpath(__file__)) + "/THE_MAYOR_OF_WHOVILLE_IN_TOWN"
            with open(path, 'wb') as fi:
                while self.transmission_ongoing:
                    data = await inner_websocket.recv()
                    fi.write(self.CHUNK)

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

    def choose_my_function(self):
        tasks = []
        tasks.append(self.print_message_angrily)
        tasks.append(self.print_message_happily)
        tasks.append(self.send_message_back)
        choice = ra.randint(0, len(tasks) - 1)
        return tasks[choice]

async def make_clients(num, address):
    clients = []
    for i in range(num):
        t = Town(address)
        clients.append(asyncio.ensure_future(t.initiate()))
    await asyncio.gather(*clients)

if __name__=="__main__":
    address = 8002
    asyncio.get_event_loop().run_until_complete(make_clients(6, address))
    asyncio.get_event_loop().run_forever()
