import os
import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

from township import Town

PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/THE_MAYOR_OF_WHOVILLE"
TEMP = PATH + "/NOTHING_TO_SEE_HERE"

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
    CONFIRMED = "Mayor will be right there!"
    DENIED = "Sorry, the mayor is indisposed at the moment"
    WAIT_RANGE = 10
    WAIT_MINIMUM = 5

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

    def get_name_of_websocket(self, websocket):
        for town in self.TOWNSHIPS:
            if self.TOWNSHIPS[town] is websocket:
                return town

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
            await self.process_mayor_request(websocket)
        logging.info("Closing connection")

    async def process_mayor_request(self, websocket):
        if os.path.exists(FILE):
            os.system("mv {} {}".format(FILE, TEMP))
            logging.info("Prepairing to send mayor")
            await websocket.send(self.helper.CONFIRMED)
            await self.send_mayor(websocket)
            logging.info("Mayor sent")
        else:
            await websocket.send(self.helper.DENIED)

    async def send_mayor(self, websocket):
        with open(TEMP, 'rb') as fi:
            while True:
                byte_chunk = fi.read(self.helper.CHUNK)
                await websocket.send(byte_chunk)
                if not byte_chunk:
                    logging.info("breaking")
                    break
        os.system("rm {}".format(TEMP))

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

    async def async_gather_functions(self, websocket):
        while True:
            logging.info("Township ticking over: {}".format(
                self.helper.get_name_of_websocket(websocket)
            ))
            wait_time = (ra.random() * self.helper.WAIT_RANGE) + self.helper.WAIT_MINIMUM
            await asyncio.sleep(wait_time)

if __name__=="__main__":
    address = 8002
    srv = Server()
    asyncio.get_event_loop().run_until_complete(srv.create_websocket_handler(address))
    asyncio.get_event_loop().run_forever()
