import pyaudio
import websockets
import asyncio
import logging

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.WARNING, format=FORMAT)
# Wav file params: channels, samplewidth, framerate, blocks, compression
# MAYOR_PARAMS = wave._wave_params(1, 1, 8000, 128000, 'NONE', 'not compressed')

class PyAudioBroadcaster:
    def __init__(self, audio_buffer):
        self.pyaudio_object = pyaudio.PyAudio()
        self.audio_buffer = audio_buffer
        self.stream = self.pyaudio_object.open(
            format=self.pyaudio_object.get_format_from_width(1),
            channels=1,
            rate=8000,
            output=True,
            start=False)

    async def write(self):
        while True:
            data = await self.audio_buffer.get()
            self.stream.write(data)

    def close(self):
        self.stream.close()
        self.pyaudio_object.terminate()

class Listener:
    CHUNK = 1024
    LISTENER_REQUEST = "I think you've assassinated the mayor! I demand to speak with them immedately!"
    def __init__(self, address):
        self.uri = "ws://localhost:{}".format(address)
        self.buf_max_size = self.CHUNK * 10
        self.audio_buffer = asyncio.Queue(maxsize=self.buf_max_size)
        self.broadcaster = PyAudioBroadcaster(self.audio_buffer)

    async def request_to_speak_with_the_mayor(self):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(self.LISTENER_REQUEST)
            transmission = []
            transmission.append(self.receive_transmission(websocket))
            transmission.append(self.broadcast_mayor())
            done, pending = await asyncio.wait(transmission,
                    return_when=asyncio.FIRST_COMPLETED)
            self.broadcaster.close()

    async def broadcast_mayor(self):
        self.broadcaster.stream.start_stream()
        await self.broadcaster.write()

    async def receive_transmission(self, websocket):
        while True:
            data = await websocket.recv()
            if not data:
                break
            await self.audio_buffer.put(data)

if __name__=="__main__":
    l = Listener(8002)
    asyncio.get_event_loop().run_until_complete(
        l.request_to_speak_with_the_mayor()
    )
