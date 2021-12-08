import pyaudio
import wave

form_1 = pyaudio.paInt16
chans = 1
sample_rate = 44100
chunk = 4096
record_secs = 3
dev_index = 1
wav_output_filename = 'test1.wav'

audio = pyaudio.PyAudio()

# create pyaudio stream object
stream = audio.open(format=form_1, rate=sample_rate, channels=chans, input_device_index=dev_index, input=True, frames_per_buffer=chunk)

print("Recording...")
frames = []

for i in range(0, (sample_rate//chunk)*record_secs):
    data = stream.read(chunk)
    frames.append(data)
    
print("Finished Recording.")

# close resources
stream.stop_stream()
stream.close()
audio.terminate()

# save wav file
wavefile = wave.open(wav_output_filename, 'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(form_1))
wavefile.setframerate(sample_rate)
wavefile.writeframes(b''.join(frames))
wavefile.close()