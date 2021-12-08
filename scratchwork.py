import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt


def wavHeader(wavefile: wave.Wave_read) -> dict:
    return {"Num Channels": wavefile.getnchannels(),
            "Sample Width": wavefile.getsampwidth(),
            "Framerate": wavefile.getframerate(),
            "Num Frames": wavefile.getnframes(),}



def main():

    print("Reading file...")
    wavefile = wave.open('test1.wav', 'rb')
    wavh = wavHeader(wavefile)
    buffer = np.frombuffer(wavefile.readframes(wavh['Num Frames']), dtype=np.int32)
    print('\t', buffer, len(buffer))

    
    print("Computing fft...")
    buffer_ft = np.fft.fft(buffer)
    x_ft = np.linspace(0, wavh['Framerate']/2, wavh['Num Frames']//2)

    print("Plotting...")
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))

    ax[0,0].plot(np.arange(len(buffer)), buffer)
    ax[0,0].set_title('Raw Data')

    ax[0,1].plot(x_ft, 2.0/wavh['Num Frames'] * np.abs(buffer_ft[:wavh['Num Frames']//2]))
    ax[0,1].set_title('FFT')
    
    plt.savefig('plot.png')
    

if __name__ == '__main__':
    main()