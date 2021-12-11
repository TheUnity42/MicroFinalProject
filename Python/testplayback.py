import pyaudio
import numpy as np

audio = pyaudio.PyAudio()

opt = {
    'format': pyaudio.paInt32,
    'chans': 1,
    'sample_rate': 48000,
    'chunk_size': 1024,
    'record_secs': 100,
    'dev_index': 1,
    'out_index': 4,
    'filename': ""
}


# create pyaudio stream object
stream = audio.open(format=opt['format'], rate=opt['sample_rate'], channels=opt['chans'],
                     input_device_index=opt['dev_index'], input=True, frames_per_buffer=opt['chunk_size'])

stream_out = audio.open(format=opt['format'], rate=opt['sample_rate'], channels=opt['chans']+1, output_device_index=opt['out_index'], output=True, frames_per_buffer=opt['chunk_size'])

frames = []

print('* recording')

for i in range(0, (opt['sample_rate']//opt['chunk_size'])*opt['record_secs']):
    data = stream.read(opt['chunk_size'])
    np_arr = np.frombuffer(data, dtype=np.int32)
    np_arr = np.repeat(np_arr, 2)
    stream_out.write(np_arr.astype(np.int32).tobytes())

print("Finished Recording.")

    # close resources
stream.stop_stream()
stream.close()
stream_out.stop_stream()
stream_out.close()
audio.terminate()
