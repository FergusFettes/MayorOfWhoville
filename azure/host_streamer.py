import argparse
import os
import wave
import pyaudio
import websockets
import asyncio
import logging
import queue

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

CHUNK = 1024
PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/transmission_file"
# Wav file params: channels, samplewidth, framerate, blocks, compression
WAV_PARAMS = wave._wave_params(1, 1, 8000, 0, 'NONE', 'not compressed')


class PyAudioStreamer:
    def __init__(self, audio_buffer):
        self.pyaudio_object = pyaudio.PyAudio()
        self.audio_buffer = audio_buffer
        self.stream = self.pyaudio_object.open(
            format=self.pyaudio_object.get_format_from_width(1),
            channels=1,
            rate=8000,
            input=True,
            start=False,
            stream_callback=self.callback,
        )

    def callback(self, in_data, frame_count, time_info, status):
        while True:
            self.audio_buffer.put(in_data)

    def close(self):
        self.stream.close()
        self.pyaudio_object.terminate()

    def start(self):
        self.stream.start_stream()

class FileStreamer:
    def __init__(self, audio_buffer):
        self.audio_buffer = audio_buffer
        self.wf = wave.open(FILE)
        self.thread = None

    def start(self):
        while True:
            while self.audio_buffer.full():
                time.sleep(0.1)
            logging.info("Writing bytes from file to buffer")
            data = self.wf.readframes(CHUNK)
            if not data:
                break
            self.audio_buffer.put(data)

    def close(self):
        self.thread.join()
        self.wf.close()

class Streamer:
    TIMEOUT = 4
    CHUNK = 1024
    CLIENT_HANDSHAKE = "How dyou do?"
    CANCEL_TRANSMISSION = "Please shutdown the connection"
    AUDIOSTREAM = "Stream coming through double quick"
    def __init__(self, address, streamer):
        self.uri = "ws://localhost:{}".format(address)
        self.name = 0
        self.buf_max_size = self.CHUNK * 10
        self.audio_buffer = queue.Queue(maxsize=self.buf_max_size)
        if streamer == "file":
            self.streamer = FileStreamer(self.audio_buffer)
        elif streamer == "pyaudio":
            self.streamer = PyAudioStreamer(self.audio_buffer)
        # elif streamer == "pysoundio":
        #     self.streamer = PySoundIoStreamer(self.audio_buffer)

    async def register_with_server(self):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(self.CLIENT_HANDSHAKE)
            self.name = await websocket.recv()
            stream = []
            stream.append(self.send_stream())
            stream.append(self.receive_message(websocket))
            stream.append(self.send_message(websocket))
            await asyncio.gather(*stream)

    async def send_stream(self):
        async with websockets.connect(self.uri) as websocket:
            logging.info("Trying to send audiostream")
            await websocket.send(self.AUDIOSTREAM)
            await websocket.send(self.name)
            await self.stream_with_timeout(websocket)
            self.streamer.close()

    async def stream_with_timeout(self, websocket):
        stream_tasks = []
        if type(self.streamer) is FileStreamer:
            stream_tasks.append(self.streamer.start())
        else:
            self.streamer.start()
        stream_tasks.append(self.forward_stream(websocket))
        stream_tasks.append(self.timeout())
        done, pending = await asyncio.wait(stream_tasks,
                return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        logging.info("Stream timed out")

    async def timeout(self):
        then = time.time()
        logging.info("Waiting for timeout")
        await asyncio.sleep(self.TIMEOUT)
        diff = time.time() - then
        logging.info("Timed out after {} seconds, returning".format(diff))

    async def forward_stream(self, websocket):
        while True:
            logging.info("Sending bytes")
            data = self.audio_buffer.get()
            if not data:
                break
            await websocket.send(data)

    async def receive_message(self, websocket):
        while True:
            message = await websocket.recv()
            logging.info("Client recieved message: {}".format(message))
            await asyncio.sleep(10)

    async def send_message(self, websocket):
        while True:
            await websocket.send("Message from client")
            logging.info("Client sent message")
            await asyncio.sleep(10)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument('--address', default=8003, type=int)
    parser.add_argument('--streamer', default='file', help='file, pyaudio or pysoundio streamer')

    args = parser.parse_args()
    s = Streamer(args.address, args.streamer)
    asyncio.get_event_loop().run_until_complete(
        s.register_with_server()
    )
