import os
import asyncio
import logging
import time
import random as ra
import websockets
import wave

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.WARNING, format=FORMAT)

from township import Town

PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/THE_MAYOR_OF_WHOVILLE"
TEMP = PATH + "/NOTHING_TO_SEE_HERE"
BACK = PATH + "/REALLY_NOTHING_TO_SEE_HERE"
MAYOR_PARAMS = wave._wave_params(1, 1, 8000, 128000, 'NONE', 'not compressed')

class ServerHelper:
    TOWNSHIPS = {
    "Whoville":[],
    "Pooville":[],
    "Notuptoyouville":[],
    "Trueville":[],
    "Flooville":[],
    "Shoeville":[],
    "Youville":[],
    "Blueville":[],
    "Screwville":[],
    "Whatatodoville":[],
    "Grueville":[],
    "Jewville":[],
    "Stewville":[],
    "Brewville":[],
    "Clueville":[],
    "Gooville":[],
    "Badooville":[],
    "Manuville":[],
    "DontmindifIdoville":[],
    "Yewville":[],
    }
    FULLSTRING = "No more towns left"
    ACTIVE_TOWNS = []
    TOWNSHIP_HANDSAKE = "I'm just a township"
    MAYOR_REQUEST = "We need to speak to the Mayor!"
    MAYOR_RETURN = "The mayor has done us a great service!"
    LISTENER_REQUEST = "I think you've assassinated the mayor! I demand to speak with them immedately!"
    TRANSMISSION_COMPLETE = "The mayor is in town!"
    MAYOR_KEEPALIVE = "We still have them, done worry!"
    CHUNK = 1024
    CONFIRMED = "Mayor will be right there!"
    DENIED = "Sorry, the mayor is indisposed at the moment"
    WAIT_RANGE = 10
    WAIT_MINIMUM = 5
    MAYOR_LOCATION = "Home"
    MAYOR_RETURN_CHANCE = 0.5

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
        self.coffers = 0
        self.keepalive_timer = time.time()
        self.transmission_ongoing = False
        # Backup the mayor, in case one of the swarm drops them during a restart
        os.system("cp {} {}".format(FILE, BACK))

    def create_websocket_handler(self, address):
        return websockets.serve(self.async_init, "localhost", address)

    async def async_init(self, websocket, path):
        handshake = await websocket.recv()
        logging.warning("Handshake: {}".format(handshake))
        if handshake == self.helper.TOWNSHIP_HANDSAKE:
            await self.main_server_activities(websocket)
        elif handshake == self.helper.MAYOR_REQUEST:
            await self.process_mayor_request(websocket)
        elif handshake == self.helper.MAYOR_RETURN:
            await self.receive_mayor(websocket)
        elif handshake == self.helper.LISTENER_REQUEST:
            self.transmission_ongoing = True
            logging.warning("Someone wants to hear the mayor! Requesting transmission")
            await self.request_transmission(websocket)
            self.transmission_ongoing = False

    async def process_mayor_request(self, websocket):
        if os.path.exists(FILE):
            os.system("mv {} {}".format(FILE, TEMP))
            logging.info("Prepairing to send mayor")
            await websocket.send(self.helper.CONFIRMED)
            name = await websocket.recv()
            await self.send_mayor(websocket)
            logging.warning("Mayor sent")
            self.helper.MAYOR_LOCATION = name
        else:
            await websocket.send(self.helper.DENIED)

    async def send_mayor(self, websocket):
        with wave.open(TEMP, 'rb') as fi:
            while True:
                byte_chunk = fi.readframes(self.helper.CHUNK)
                await websocket.send(byte_chunk)
                if not byte_chunk:
                    break
        os.system("rm {}".format(TEMP))

    async def receive_mayor(self, inner_websocket):
        with wave.open(TEMP, 'wb') as fi:
            fi.setparams(MAYOR_PARAMS)
            while True:
                data = await inner_websocket.recv()
                if not data:
                    break
                fi.writeframes(data)
        os.system("mv {} {}".format(TEMP, FILE))
        self.helper.MAYOR_LOCATION = "Home"

    async def request_transmission(self, websocket):
        mayor_websocket = self.helper.TOWNSHIPS[self.helper.MAYOR_LOCATION]
        await mayor_websocket.send(self.helper.LISTENER_REQUEST)
        await websocket.send("The mayor will be with you soon, transmitting directly from {}!".format(self.helper.MAYOR_LOCATION))
        await self.pass_transmission_to(websocket, mayor_websocket)

    async def pass_transmission_to(self, listener_websocket, mayor_websocket):
        logging.info("Passing transmission")
        while True:
            data = await mayor_websocket.recv()
            await listener_websocket.send(data)
            if not data:
                break

    async def main_server_activities(self, websocket):
        name = self.helper.assign_connection_to_town(websocket)
        if name == self.helper.FULLSTRING:
            raise
        await self.assign_name(websocket, name)
        try:
            while True:
                await self.async_gather_functions(websocket)
        finally:
            self.helper.remove_connection_from_town(websocket)
            logging.warning("{} has disconnected!".format(name))

    async def assign_name(self, websocket, name):
        await websocket.send(name)
        logging.warning("{} has been assigned!".format(name))

    async def async_gather_functions(self, websocket):
        tasks = []
        tasks.append(self.mayor_manager(websocket))
        tasks.append(self.mayor_keepalive(websocket))
        tasks.append(self.recieve_message(websocket))
        tasks.append(self.send_gold(websocket))
        await asyncio.gather(*tasks)

    async def mayor_manager(self, websocket):
        websocket_name = self.helper.get_name_of_websocket(websocket)
        if websocket_name == self.helper.MAYOR_LOCATION:
            if self.transmission_ongoing:
                pass
            elif ra.random() < self.helper.MAYOR_RETURN_CHANCE:
                logging.info("Demanding return of mayor!")
                await websocket.send(self.helper.MAYOR_RETURN)
        else:
            logging.info("Township ticking over: {}".format(
            self.helper.get_name_of_websocket(websocket)
        ))
        wait_time = (ra.random() * self.helper.WAIT_RANGE) + self.helper.WAIT_MINIMUM
        await asyncio.sleep(wait_time)

    async def mayor_keepalive(self, websocket):
        if os.path.exists(FILE):
            self.keepalive_timer = time.time()
        now = time.time() - self.keepalive_timer
        if now > self.helper.WAIT_RANGE * 2:
            logging.error("Noone has heard from the mayor in {} seconds!".format(now))
            if now > self.helper.WAIT_RANGE * 4:
                logging.critical("The mayor has vanished! Resurrecting.")
                os.system("cp {} {}".format(BACK, FILE))
        await asyncio.sleep(self.helper.WAIT_RANGE)

    async def recieve_message(self, websocket):
        if self.transmission_ongoing:
            await asyncio.sleep(self.helper.WAIT_RANGE)
        else:
            message = await websocket.recv()
            if message == self.helper.MAYOR_KEEPALIVE:
                self.keepalive_timer = time.time()
                logging.info("Keepalive reset!")
            else:
                await self.recieve_gold(message, websocket)

    async def recieve_gold(self, income, websocket):
        logging.warning("Recieved {} from {}! This will help out some needy people".format(income, self.helper.get_name_of_websocket(websocket)))
        self.coffers += int(income)

    async def send_gold(self, websocket):
        if self.transmission_ongoing:
            await asyncio.sleep(self.helper.WAIT_RANGE)
        else:
            if self.coffers:
                amount = self.coffers // 5
                await websocket.send(str(amount))
                logging.warning("Send {} to {}!".format(amount, self.helper.get_name_of_websocket(websocket)))
                self.coffers -= amount



if __name__=="__main__":
    address = 8002
    srv = Server()
    asyncio.get_event_loop().run_until_complete(srv.create_websocket_handler(address))
    asyncio.get_event_loop().run_forever()
