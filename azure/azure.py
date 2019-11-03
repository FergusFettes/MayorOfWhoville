import wave
import os
import asyncio
import logging
import websockets

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.WARNING, format=FORMAT)

PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/output.wav"
# Wav file params: channels, samplewidth, framerate, blocks, compression
WAV_PARAMS = wave._wave_params(1, 1, 8000, 128000, 'NONE', 'not compressed')

class StreamTranscriber:
    CHUNK = 1024
    CLIENT_HANDSHAKE = "How dyou do?"
    CANCEL_TRANSMISSION = "Please shutdown the connection"
    AUDIOSTREAM = "Stream coming through double quick"

    def __init__(self):
        self.CONNECTED = {}
        self.CHILDREN = {}

    def setup_server(self, address):
        return websockets.serve(self.async_init, "localhost", address)

    async def async_init(self, websocket, path):
        handshake = await websocket.recv()
        if handshake == self.CLIENT_HANDSHAKE:
            await self.main_server_activities(websocket)
        elif handshake == self.AUDIOSTREAM:
            parent = await webocket.recv()
            if parent in self.CONNECTED.keys():
                self.CHILDREN[self.CONNECTED[parent]] = websocket
                await self.receive_stream(websocket)

    async def receive_stream(self, websocket):
        with wave.open(FILE, 'wb') as fi:
            fi.setparams(WAV_PARAMS)
            while True:
                data = await websocket.recv()
                if not data:
                    break
                fi.writeframes(data)

    async def main_server_activities(self, websocket):
        await self.identify(websocket)
        try:
            await self.main_server_functions(self, websocket)
        finally:
            self.CONNECTED.pop(socketid)

    async def identify(self, websocket):
        socketid = hash(websocket)
        self.CONNECTED[str(socketid)] = websocket
        await websocket.send(str(socketid))

    async def main_server_functions(self, websocket):
        activities = []
        activities.append(self.receive_message(websocket))
        activities.append(self.send_message(websocket))
        done, pending = await asyncio.wait(activities,
                return_when=asyncio.FIRST_COMPLETED)
        for activity in pending:
            activity.cancel()
        # The other main setup, when you want them all to happen simultaneously and dont care when then return
        # await asyncio.gather(*activities)

    async def receive_message(self, websocket):
        while True:
            message = await websocket.recv()
            logging.info("Server received message: {}".format(message))
            if message == self.CANCEL_TRANSMISSION:
                for websocket in self.CHILDREN[websocket]:
                    websocket.close()

    async def send_message(self, websocket):
        while True:
            whatever = "whatever"
            await websocket.send(whatever)
            logging.info("Sent {} to client".format(whatever))

if __name__=="__main__":
    address = 8003
    st = StreamTranscriber()
    asyncio.get_event_loop().run_until_complete(st.setup_server(address))
    asyncio.get_event_loop().run_forever()
