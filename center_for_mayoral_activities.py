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

class Server:
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

    def main(self, address):
        async def handler(websocket, path):
            handshake = await websocket.recv()
            if handshake == self.TOWNSHIP_HANDSAKE:
                name = self.assign_connection_to_town(websocket)
                if name == self.FULLSTRING:
                    raise
                await township_loop(websocket, name)
            elif handshake == self.MAYOR_REQUEST:
                name = await websocket.recv()
                parent_websocket = self.TOWNSHIPS[name]
                await send_mayor(websocket, self.CHUNK)
                await parent_websocket.send(self.TRANSMISSION_COMPLETE)
                logging.info("Mayor sent")

        async def send_mayor(websocket, chunk):
            with open(PATH, 'rb') as fi:
                while True:
                    byte_chunk = fi.read(chunk)
                    if not byte_chunk:
                        break
                    await websocket.send(byte_chunk)

        async def township_loop(websocket, name):
            await assign_name(websocket, name)
            try:
                await main(websocket)
            finally:
                self.remove_connection_from_town(websocket)
                logging.info("{} has disconnected!".format(name))

        async def assign_name(websocket, name):
            await websocket.send(name)
            logging.info("{} has been assigned!".format(name))

        async def send_message(websocket):
            while True:
                await asyncio.sleep(ra.random() * 3)
                await websocket.send("toasties")

        async def process_message(websocket):
            while True:
                message = await websocket.recv()
                logging.info("Server got a message: {}".format(message))

        async def main(websocket):
            tasks = []
            tasks.append(process_message(websocket))
            tasks.append(send_message(websocket))
            await asyncio.gather(*tasks)

        return websockets.serve(handler, "localhost", address)

if __name__=="__main__":
    address = 8002
    srv = Server()
    asyncio.get_event_loop().run_until_complete(srv.main(address))
    asyncio.get_event_loop().run_forever()
