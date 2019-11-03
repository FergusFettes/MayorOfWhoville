import argparse
import time
import os
import wave
import pyaudio
import pysoundio
import websockets
import asyncio
import logging
import queue

FORMAT = "%(levelname)s%(asctime)s -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

CHUNK = 1024
PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/transmission_file"
# Wav file params: channels, samplewidth, framerate, blocks, compression
WAV_PARAMS = wave._wave_params(1, 1, 8000, 0, 'NONE', 'not compressed')


class PySoundIoStreamer:
    def __init__(self):
        self.CHUNK = 1024
        self.pysoundio_object = pysoundio.PySoundIo(backend=None)
        self.params = "1,2,44100"
        self.buffer = queue.Queue(maxsize=CHUNK * 50)
        logging.info("Starting stream")
        self.pysoundio_object.start_input_stream(
            device_id=None,
            channels=1,
            sample_rate=44100,
            block_size=self.CHUNK,
            dtype=pysoundio.SoundIoFormatS16LE,
            read_callback=self.callback,
        )

    def callback(self, data, length):
        logging.info("Dumping data")
        self.buffer.put(data)

    async def stream_to_websocket(self, websocket):
        while True:
            data = self.buffer.get()
            await websocket.send(data)
            logging.info("Writing data")

    def overflow(self):
        logging.warning("Overflow imminent!")

    def close(self):
        self.pysoundio_object.close()

class Streamer:
    TIMEOUT = 4
    def __init__(self, address, streamer):
        self.uri = "ws://localhost:{}".format(address)
        self.streamer = PySoundIoStreamer()

    async def register_with_server(self):
        async with websockets.connect(self.uri) as websocket:
            logging.warning("Starting stream transmission")
            await self.stream_over_websockets(websocket)
            self.streamer.close()
            logging.warning("Stream transmission ended")

    async def stream_over_websockets(self, websocket):
        await websocket.send(self.streamer.params)
        while True:
            await self.streamer.stream_to_websocket(websocket)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument('--address', default=8003, type=int)
    parser.add_argument('--streamer', default='file', help='file, pyaudio or pysoundio streamer')

    args = parser.parse_args()
    s = Streamer(args.address, args.streamer)
    asyncio.get_event_loop().run_until_complete(
        s.register_with_server()
    )
