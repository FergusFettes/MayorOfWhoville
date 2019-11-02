import os
import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

PATH = os.path.dirname(os.path.realpath(__file__)) + "/THE_MAYOR_OF_WHOVILLE_IN_TOWN"

class Town:
    MAYOR_REQUEST = "We need to speak to the Mayor!"
    TRANSMISSION_COMPLETE = "The mayor is in town!"
    TOWNSHIP_HANDSAKE = "I'm just a township"
    MAYOR_OUT = "Sorry, the mayor is out on important business"
    def __init__(self, address):
        self.uri = "ws://localhost:{}".format(address)
        self.name = ''

    async def initiate(self):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(self.TOWNSHIP_HANDSAKE)
            self.name = await websocket.recv()
            logging.info("I have a name! My name is {}".format(self.name))
            while True:
                func = self.choose_my_function()
                await func(websocket)
                logging.info("Process complete, should be starting a new one?")
                await asyncio.sleep(1)

    async def process_mayoral_transmission(self, websocket):
        reciever = asyncio.ensure_future(self.request_mayor())
        ender = asyncio.ensure_future(self.wait_for_transmission_end(websocket))
        done, pending = await asyncio.wait(
            [reciever, ender],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

    async def wait_for_transmission_end(self, websocket):
        logging.info("Waiting for response from CMA")
        while True:
            message = await websocket.recv()
            logging.info(message)
            if message == self.TRANSMISSION_COMPLETE:
                logging.info("Transmission successful, waiting completion")
                await asyncio.sleep(10)
                logging.info("Finished waiting completion")
            elif message == self.MAYOR_OUT:
                logging.info("Mayor is out on business! Shutting down")
                break
            else:
                logging.info("Processor got a message, unrelated to its currently deeply important duties and promptly disregarded it")

    async def request_mayor(self):
        async with websockets.connect(self.uri) as inner_websocket:
            try:
                await inner_websocket.send(self.MAYOR_REQUEST)
                await inner_websocket.send(self.name)
                await receive_mayor(inner_websocket)
            except:
                logging.info("Reciever was shutdown")
        logging.info("Mayor receiver quit of its own accord!")

    async def receive_mayor(inner_websocket):
            with open(PATH, 'wb') as fi:
                while True:
                    data = await inner_websocket.recv()
                    logging.info(data)
                    await asyncio.sleep(0.1)
                    if not data:
                        break
                    fi.write(data)

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
        # tasks.append(self.print_message_angrily)
        # tasks.append(self.print_message_happily)
        # tasks.append(self.send_message_back)
        tasks.append(self.process_mayoral_transmission)
        choice = ra.randint(0, len(tasks) - 1)
        return tasks[choice]

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
