import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt


def wavHeader(wavefile: wave.Wave_read) -> dict:
    return {"Num Channels": wavefile.getnchannels(),
            "Sample Width": wavefile.getsampwidth(),
            "Framerate": wavefile.getframerate(),
            "Num Frames": wavefile.getnframes(),}

EPSILON = 1e-12

def main():

    print("Reading file...")
    # wave.open('Roland-D-20-8-Beat-1-112-bpm.wav', 'rb')
    wavefile = wave.open('wavefile.wav', 'rb')
    wavh = wavHeader(wavefile)

    print(wavh)

    buffer = np.frombuffer(wavefile.readframes(wavh['Num Frames']), dtype=np.int16)

    # buffer = buffer / buffer.max() * 1000

    print('\t', buffer, len(buffer))

    
    print("Computing fft...")
    buffer_ft = np.fft.fft(buffer)
    x_ft = np.linspace(0, wavh['Framerate']/2, wavh['Num Frames']//2)

    print("Computing Spectogram...")
    N = 256
    buffer_s = []
    for k in np.arange(0, wavh['Num Frames'], N):
        x = np.fft.fftshift(np.fft.fft(buffer[k:k+N], N))[N//2:N]
        Pxx = 10*np.log10(np.real(x*np.conj(x))+EPSILON)
        buffer_s.append(Pxx)

    buffer_s = np.array(buffer_s)


    print("Plotting...")
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))

    ax[0,0].plot(np.arange(len(buffer)), buffer)
    ax[0,0].set_title('Raw Data')

    ax[0,1].plot(x_ft, 2.0/wavh['Num Frames'] * np.abs(buffer_ft[:wavh['Num Frames']//2]))
    ax[0,1].set_title('FFT')

    ax[1,0].specgram(buffer_s[:,0])
    ax[1,0].set_title('Spectrogram')
    
    plt.savefig('plot.png')

    print(buffer.max(), buffer.min(), buffer.std())
    

if __name__ == '__main__':
    main()
