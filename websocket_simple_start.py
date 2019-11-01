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



async def send_message(websocket, path):
    while True:
        await asyncio.sleep(ra.random() * 3)
        await websocket.send("buttholes")


def return_server(address):
    return websockets.serve(send_message, "localhost", address)

async def server_and_clients(address):
    tasks = []
    tasks.append(return_server(address))
    tasks.append(print_message_angrily(address))
    tasks.append(print_message_happily(address))
    await asyncio.gather(*tasks)

if __name__=="__main__":
    address = 8002
    asyncio.get_event_loop().run_until_complete(server_and_clients(address))
    asyncio.get_event_loop().run_forever()
