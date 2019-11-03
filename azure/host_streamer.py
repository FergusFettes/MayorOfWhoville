import os
import wave
import pyaudio
import websockets
import asyncio
import logging

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

CHUNK = 1024
PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/transmission_file.wav"
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

    async def callback(self, in_data, frame_count, time_info, status):
        while True:
            await self.audio_buffer.put(in_data)

    def close(self):
        self.stream.close()
        self.pyaudio_object.terminate()

    def start(self):
        self.stream.start_stream()

class FileStreamer:
    def __init__(self, audio_buffer):
        self.audio_buffer = audio_buffer
        wf = wave.open(FILE)

    async def start(self):
        while True:
            data = wf.readframes(CHUNK)
            if not data:
                break
            await self.audio_buffer.put(data)

    def close(self):
        wf.close()

class Streamer:
    TIMEOUT = 10
    CHUNK = 1024
    CLIENT_HANDSHAKE = "How dyou do?"
    CANCEL_TRANSMISSION = "Please shutdown the connection"
    AUDIOSTREAM = "Stream coming through double quick"
    def __init__(self, address):
        self.uri = "ws://localhost:{}".format(address)
        self.name = 0
        self.buf_max_size = self.CHUNK * 10
        self.audio_buffer = asyncio.Queue(maxsize=self.buf_max_size)
        self.streamer = FileStreamer(self.audio_buffer)

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
            await websocket.send(self.AUDIOSTREAM)
            await websocket.send(self.name)
            self.streamer.start()
            await self.stream_with_timeout(websocket)
            self.streamer.close()

    async def stream_with_timeout(self, websocket):
        stream_tasks = []
        stream_tasks.append(self.forward_stream(websocket))
        stream_tasks.append(asyncio.sleep(self.TIMEOUT))
        done, pending = await asyncio.wait(stream_tasks,
                return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            stream.cancel()

    async def forward_stream(self, websocket):
        while True:
            await websocket.send(self.audio_buffer.get())

    async def receive_message(self, websocket):
        while True:
            message = await websocket.recv()
            logging.info("Recieved message: {}".format(message))
            await asyncio.sleep(10)

    async def send_message(self, websocket):
        pass
        #Can put a ping in here, or a command to end the audiostream under certain circumstances


if __name__=="__main__":
    s = Streamer(8003)
    asyncio.get_event_loop().run_until_complete(
        s.register_with_server()
    )
