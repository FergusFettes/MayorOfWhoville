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
        logging.warning("Stream received, disconnecting")

    async def receive_stream(self, websocket):
        # name = "{}_{}.wav".format(FILE, str(hash(websocket)))
        name = FILE + ".wav"
        params = await websocket.recv()
        params = params.split(',')
        params = [int(i) for i in params]
        special = await websocket.recv()
        if special == "True":
            await self.pysoundio_func(websocket, params)
        else:
            with wave.open(name, 'wb') as fi:
                fi.setnchannels(params[0])
                fi.setsampwidth(params[1])
                fi.setframerate(params[2])
                while True:
                    data = await websocket.recv()
                    logging.info("Bytes received")
                    if not data:
                        logging.info("Empty packet received, closing")
                        break
                    fi.writeframes(data)

    async def pysoundio_func(self, websocket, params):
        wav_file = sf.SoundFile(
            FILE + ".wav", mode='w', channels=params[0],
            samplerate=params[2]
        )
        while True:
            data = await websocket.recv()
            if not data:
                break
            wav_file.buffer_write(data, dtype='float32')
        wav_file.close()

if __name__=="__main__":
    address = 8003
    st = StreamTranscriber()
    asyncio.get_event_loop().run_until_complete(st.setup_server(address))
    asyncio.get_event_loop().run_forever()
