import asyncio
import logging
import time
import random as ra
import websockets

FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)


async def print_message_angrily(address):
    uri = "ws://localhost:{}".format(address)
    async with websockets.connect(uri) as websocket:
        while True:
            await asyncio.sleep(ra.random() * 3)
            message = await websocket.recv()
            logging.info("Fuckin {}!".format(message))

async def print_message_happily(address):
    uri = "ws://localhost:{}".format(address)
    async with websockets.connect(uri) as websocket:
        while True:
            await asyncio.sleep(ra.random() * 3)
            message = await websocket.recv()
            logging.info("Love those {}!".format(message))

async def send_message_back(address):
    uri = "ws://localhost:{}".format(address)
    async with websockets.connect(uri) as websocket:
        while True:
            await asyncio.sleep(ra.random() * 3)
            await websocket.send("hello servi!")

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

    def assign_connection_to_town(self, websocket):
        for town in self.TOWNSHIPS:
            if not self.TOWNSHIPS[town]:
                self.TOWNSHIPS[town] = websocket
                return town
        return self.FULLSTRING

    def remove_connection_from_town(self, websocket):
        for town in self.TOWNSHIPS:
            if self.TOWNSHIPS[town] is websocket:
                self.TOWNSHIPS[town] = []

    def main(self, address):
        async def handler(websocket, path):
            name = self.assign_connection_to_town(websocket)
            if name == self.FULLSTRING:
                raise
            logging.info(self.TOWNSHIPS)
            try:
                await main(websocket, path)
            finally:
                self.remove_connection_from_town(websocket)
                logging.log(self.TOWNSHIPS)

        async def send_message(websocket, path):
            while True:
                await asyncio.sleep(ra.random() * 3)
                await websocket.send("toasties")

        async def process_message(websocket, path):
            while True:
                message = await websocket.recv()
                logging.info("Server got a message: {}".format(message))

        async def main(websocket, path):
            tasks = []
            tasks.append(process_message(websocket, path))
            tasks.append(send_message(websocket, path))
            await asyncio.gather(*tasks)

        return websockets.serve(handler, "localhost", address)

async def server_and_clients(address):
    tasks = []
    srv = Server()
    tasks.append(srv.main(address))
    tasks.append(print_message_angrily(address))
    tasks.append(print_message_happily(address))
    tasks.append(send_message_back(address))
    await asyncio.gather(*tasks)

if __name__=="__main__":
    address = 8002
    asyncio.get_event_loop().run_until_complete(server_and_clients(address))
    asyncio.get_event_loop().run_forever()
