import os
import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

from township import Town

PATH = os.path.dirname(os.path.realpath(__file__)) + "/THE_MAYOR_OF_WHOVILLE"

class ServerHelper:
    TOWNSHIPS = {
    "Whoville":[],
    "Pooville":[],
    "Trueville":[],
    "Flooville":[],
    "Shoeville":[],
    "Blueville":[],
    "Screwville":[],
    "Whatatodoville":[],
    "Grueville":[],
    "Jewville":[],
    "Stewville":[],
    "Brewville":[],
    "Gooville":[],
    }
    FULLSTRING = "No more towns left"
    ACTIVE_TOWNS = []
    TOWNSHIP_HANDSAKE = "I'm just a township"
    MAYOR_REQUEST = "We need to speak to the Mayor!"
    TRANSMISSION_COMPLETE = "The mayor is in town!"
    CHUNK = 1024
    MAYOR_PRESENT = True
    MAYOR_OUT = "Sorry, the mayor is out on important business"
    def assign_connection_to_town(self, websocket):
        possible_towns = []
        for town in self.TOWNSHIPS:
            if not self.TOWNSHIPS[town]:
                possible_towns.append(town)
        if not len(possible_towns):
            return self.FULLSTRING
        choice = possible_towns[ra.randint(0, len(possible_towns) - 1)]
        self.TOWNSHIPS[choice] = websocket
        self.ACTIVE_TOWNS.append(choice)
        return choice

    def remove_connection_from_town(self, websocket):
        for town in self.TOWNSHIPS:
            if self.TOWNSHIPS[town] is websocket:
                self.TOWNSHIPS[town] = []
                self.ACTIVE_TOWNS.remove(town)

    def choose_random_active_town(self):
        choice = ra.randint(0, len(self.ACTIVE_TOWNS) - 1)
        return self.TOWNSHIPS[self.ACTIVE_TOWNS[choice]]

class Server:
    def __init__(self):
        self.helper = ServerHelper()

    def create_websocket_handler(self, address):
        return websockets.serve(self.async_init, "localhost", address)

    async def async_init(self, websocket, path):
        handshake = await websocket.recv()
        logging.info("Handshake: {}".format(handshake))
        if handshake == self.helper.TOWNSHIP_HANDSAKE:
            await self.main_township_loop(websocket)
        elif handshake == self.helper.MAYOR_REQUEST:
            await self.process_mayor_request(websocket, self.helper.CHUNK)
        logging.info("Closing connection")

    async def process_mayor_request(self, websocket, chunk):
        if self.helper.MAYOR_PRESENT:
            logging.info("Prepairing to send mayor")
            self.helper.MAYOR_PRESENT = False

            parent_websocket_name = await websocket.recv()
            parent_websocket = self.helper.TOWNSHIPS[parent_websocket_name]

            await self.send_mayor(websocket, chunk)

            await parent_websocket.send(self.helper.TRANSMISSION_COMPLETE)
            logging.info("Mayor sent")
        else:
            logging.info("Mayor not about, sending shutdown")
            parent_websocket_name = await websocket.recv()
            parent_websocket = self.helper.TOWNSHIPS[parent_websocket_name]
            await parent_websocket.send(self.helper.MAYOR_OUT)

    async def send_mayor(self, websocket, chunk):
        with open(PATH, 'rb') as fi:
            while True:
                byte_chunk = fi.read(chunk)
                logging.info(byte_chunk)
                await asyncio.sleep(0.1)
                await websocket.send(byte_chunk)
                if not byte_chunk:
                    break
        os.system("rm {}".format(PATH))

    async def main_township_loop(self, websocket):
        name = self.helper.assign_connection_to_town(websocket)
        if name == self.helper.FULLSTRING:
            raise
        await self.assign_name(websocket, name)
        try:
            await self.async_gather_functions(websocket)
        finally:
            self.helper.remove_connection_from_town(websocket)
            logging.info("{} has disconnected!".format(name))

    async def assign_name(self, websocket, name):
        await websocket.send(name)
        logging.info("{} has been assigned!".format(name))

    async def send_message(self, websocket):
        while True:
            await asyncio.sleep(ra.random() * 3)
            await websocket.send("toasties")

    async def process_message(self, websocket):
        while True:
            message = await websocket.recv()
            logging.info("Server got a message: {}".format(message))

    async def async_gather_functions(self, websocket):
        tasks = []
        tasks.append(self.process_message(websocket))
        tasks.append(self.send_message(websocket))
        await asyncio.gather(*tasks)

if __name__=="__main__":
    address = 8002
    srv = Server()
    asyncio.get_event_loop().run_until_complete(srv.create_websocket_handler(address))
    asyncio.get_event_loop().run_forever()
