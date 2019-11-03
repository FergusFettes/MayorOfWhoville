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

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

CHUNK = 1024
PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/transmission_file"
# Wav file params: channels, samplewidth, framerate, blocks, compression
WAV_PARAMS = wave._wave_params(1, 1, 8000, 0, 'NONE', 'not compressed')


class PyAudioStreamer:
    def __init__(self):
        self.pyaudio_object = pyaudio.PyAudio()
        self.params = "1,2,44100"
        self.stream = self.pyaudio_object.open(
            channels=1,
            format=pyaudio.paInt16,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )
    def close(self):
        self.stream.close()
        self.pyaudio_object.terminate()

class PySoundIoStreamer:
    def __init__(self):
        self.pysoundio_object = pysoundio.PySoundIo(backend=None)
        self.params = "1,1,44100"
        self.buffer = queue.Queue(maxsize=CHUNK * 10)
        class Stream: pass
        self.stream = Stream()
        self.stream.read = self.buffer.get()
        self.pysoundio_object.start_input_stream(
            device_id=None,
            channels=1,
            sample_rate=44100,
            block_size=1024,
            dtype=pysoundio.SoundIoFormatU8,
            read_callback=self.callback
        )

    def callback(self, data, length):
        self.audio_buffer.put(data)

    def close(self):
        self.pysoundio_object.close()

class FileStreamer:
    def __init__(self):
        self.wf = wave.open(FILE)
        self.params = "1,1,8000"
        class Stream: pass
        self.stream = Stream()
        self.stream.read = self.wf.readframes

    def close(self):
        self.wf.close()

class Streamer:
    TIMEOUT = 4
    CLIENT_HANDSHAKE = "How dyou do?"
    CANCEL_TRANSMISSION = "Please shutdown the connection"
    AUDIOSTREAM = "Stream coming through double quick"
    def __init__(self, address, streamer):
        self.uri = "ws://localhost:{}".format(address)
        self.name = 0
        self.buf_max_size = CHUNK * 10
        if streamer == "file":
            self.streamer = FileStreamer()
        elif streamer == "pyaudio":
            self.streamer = PyAudioStreamer()
        elif streamer == "pysoundio":
            self.streamer = PySoundIoStreamer()

    async def register_with_server(self):
        async with websockets.connect(self.uri) as websocket:
            logging.warning("Starting stream transmission")
            await self.stream_with_timeout(websocket)
            self.streamer.close()
            logging.warning("Stream transmission ended successfully")

    async def stream_with_timeout(self, websocket):
        await websocket.send(self.streamer.params)
        while True:
            logging.info("Sending bytes")
            data = self.streamer.stream.read(CHUNK)
            if not data:
                break
            await websocket.send(data)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument('--address', default=8003, type=int)
    parser.add_argument('--streamer', default='file', help='file, pyaudio or pysoundio streamer')

    args = parser.parse_args()
    s = Streamer(args.address, args.streamer)
    asyncio.get_event_loop().run_until_complete(
        s.register_with_server()
    )
