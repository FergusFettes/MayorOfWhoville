import soundfile as sf
import wave
import os
import asyncio
import logging
import websockets

FORMAT = "%(levelname)s -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

PATH = os.path.dirname(os.path.realpath(__file__))
FILE = PATH + "/output"
# Wav file params: channels, samplewidth, framerate, blocks, compression
WAV_PARAMS = wave._wave_params(1, 1, 8000, 128000, 'NONE', 'not compressed')

class StreamTranscriber:
    def setup_server(self, address):
        return websockets.serve(self.async_init, "localhost", address)

    async def async_init(self, websocket, path):
        logging.warning("Prepairing to receive stream")
        await self.receive_stream(websocket)
        logging.warning("Stream finished, disconnecting")

    async def receive_stream(self, websocket):
        # name = "{}_{}.wav".format(FILE, str(hash(websocket)))
        name = FILE + ".wav"
        params = await websocket.recv()
        params = params.split(',')
        params = [int(i) for i in params]
        choice = await websocket.recv()
        if choice == "wav":
            await self.write_with_wav(websocket, params)
        else:
            await self.pysoundio_func(websocket, params)

    async def write_with_wav(self, websocket, params):
        with wave.open(FILE + ".wav", 'wb') as fi:
            fi.setnchannels(params[0])
            fi.setsampwidth(params[1])
            fi.setframerate(params[2])
            while True:
                data = await websocket.recv()
                logging.info("Bytes received")
                fi.writeframes(data)

    async def pysoundio_func(self, websocket, params):
        wav_file = sf.SoundFile(
            FILE + ".wav", mode='w', channels=params[0],
            samplerate=params[2]
        )
        while True:
            data = await websocket.recv()
            logging.info("Bytes received")
            wav_file.buffer_write(data, dtype='int16')
        wav_file.close()

if __name__=="__main__":
    address = 8003
    st = StreamTranscriber()
    asyncio.get_event_loop().run_until_complete(st.setup_server(address))
    asyncio.get_event_loop().run_forever()
