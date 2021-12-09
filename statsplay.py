import numpy as np
import pyaudio
import wave
import sys
import getopt
import matplotlib.pyplot as plt
import threading
import time
import logging


class AtomicArray:
    def __init__(self, size):
        self.size = size
        self.array = np.zeros(size)
        self._lock = threading.Lock()

    def set(self, value):
        with self._lock:
            self.array = value

    def append(self, value):
        with self._lock:
            self.array = np.append(self.array, value)

    def get(self):
        with self._lock:
            return self.array

def play_audio(config: dict, raise_exception):
    """
        Plays an audio file

        Parameters
        ----------
        config : dictionary of configuration parameters
            - filename : string
                path to the audio file to be played
            - device : int
                device index to be used for playback
            - volume : float
                volume of the audio file to be played
            - channels : int
                number of channels of the audio file to be played
            - rate : int
                sampling rate of the audio file to be played
            - chunk : int
                size of the chunks of the audio file to be played
            - duration : float - NOT USED
                duration of the audio file to be played
            - array: AtomicArray
                array to append chunk data to
            - effects: dict
                dictionary of effects to be applied to the audio file
    
        raise_exception : function
            if True, will halt the thread

        Returns
        -------
        nothing
        """
    wf = wave.open(config['filename'], 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
        output_device_index=config['device']
    )

    data = wf.readframes(config['chunk'])

    def fadefunc(x, rate=2):
        """
        Channel fade function.

        Parameters
        ----------
        x : ndarray of sample positions
        rate : rate of fade in samples

        Returns
        -------
        ndarray of values 0-1, for relative fade between left and right channels
        """
        return (np.sin(rate * x * np.pi / wf.getframerate()) + 1) / 2

    def exp_distort(v, window=2):
        """
        Exponential distortion function.

        Parameters
        ----------
        x : ndarray of sample positions
        rate : rate of distortion in samples

        Returns
        -------
        ndarray of values 0-1, for relative distortion
        """
        ratio = 1 - np.exp(v-window) - np.exp(-v-window)
        return ratio

    last_max = 0

    # stores the position of each sample (in frames)
    count = np.arange(0, config['chunk'])

    while len(data) > 0:
        # read data from buffer into a mutable numpy array
        buffer = np.frombuffer(data, dtype=np.int16).copy()

        max_value = np.max(np.abs(buffer))
        if max_value > last_max:
            last_max = max_value
        else:
            last_max = (last_max * (1 - config['effects']['volume_roll_rate'])) + (
                max_value * config['effects']['volume_roll_rate'])

        buffer = buffer / last_max

        # isolates the left channel. [::2] will take every other element, starting at 0
        left = buffer[::2]
        # isolates the right channel. [1::2] will take every other element, starting at 1
        right = buffer[1::2]

        fade = fadefunc(count, 2)[:len(buffer) // 2]
        count += config['chunk']

        # multiply the left and right channels by the fade value
        # left[:] will modify the left channel in place, mutating the original buffer array
        # note the cast to np.int16, numpy really wants it to be a float32
        # left[:] = (left[:] * fade)
        # right[:] will modify the right channel in place, mutating the original buffer array
        # right[:] = (right[:] * (1-fade))

        # distort the output
        distort = exp_distort(buffer, 2)[:len(buffer)]
        buffer = buffer * distort

        config['array'].append(buffer)

        buffer *= config['volume']

        # buffer tobytes() will convert the now mutated buffer array back to a python bytes object
        # stream.write() will play the entire buffer (chunksize bytes)
        stream.write(buffer.astype(np.int16, copy=False).tobytes())

        if raise_exception():
            raise Exception("InteruptException in playback thread")

        # read the next chunk of data from the file
        data = wf.readframes(config['chunk'])

    print("* done *")

    stream.stop_stream()
    stream.close()
    p.terminate()


def subsample(array, factor, method='mean'):
    """
    Subsample an array by a factor. Using the given method
    """
    if method == 'mean':
        return np.mean(array.reshape(-1, factor), axis=1)
    elif method == 'median':
        return np.median(array.reshape(-1, factor), axis=1)
    else:
        raise ValueError('Method not supported')


def nearestEvenDenominator(number, denominator):
    """
    Returns the nearest even denominator of the given number that produces no remainder
    """
    while number % denominator != 0:
        denominator -= 1
    return denominator

def run(config, data_array):
    raise_exception = False

    def handle_close_event(event): # FIXME: why this no worky?
        global raise_exception
        raise_exception = True

    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    fig.tight_layout(pad=3)

    fig.canvas.mpl_connect('close_event', handle_close_event)

    playback_thread = threading.Thread(target=play_audio, args=(
        config, lambda: raise_exception), daemon=True)   


    sliding_window_size = 50000
    window_subsample_rate = 64
    plot_sample_rate = 100

    ax[0].set_xlabel('Frames')
    ax[0].set_ylabel('Amplitude')
    ax[0].set_title('Audio Signal - Left')
    ax[0].set_ylim([-1, 1])
    ax[0].set_xlim([0, sliding_window_size//(2*window_subsample_rate)])

    ax[1].set_xlabel('Frames')
    ax[1].set_ylabel('Amplitude')
    ax[1].set_title('Audio Signal - Right')
    ax[1].set_ylim([-1, 1])
    ax[1].set_xlim([0, sliding_window_size//(2*window_subsample_rate)])

    plot_points_left = ax[0].plot(np.arange(sliding_window_size//2), np.zeros(sliding_window_size//2))[0]
    plot_points_right = ax[1].plot(np.arange(sliding_window_size//2), np.zeros(sliding_window_size//2))[0]
    
    plt.ion()
    plt.show()
    plt.pause(0.1)

    config['effects'] = {}
    config['effects']['volume_roll_rate'] = 0.05


    time.sleep(0.5)
    playback_thread.start()

    # cache background
    background = fig.canvas.copy_from_bbox(ax[0].bbox)


    try:
        while playback_thread.is_alive():
            # update the data
            window_data_left = subsample(data_array.get()[-sliding_window_size::2], 2)

            plot_points_left.set_data(
                np.arange(window_data_left.shape[0]), window_data_left)

            window_data_right = subsample(data_array.get()[-sliding_window_size+1::2], 2)

            plot_points_right.set_data(np.arange(window_data_right.shape[0]), window_data_right)

            # rebuild plot
            fig.canvas.restore_region(background)
            ax[0].draw_artist(plot_points_left)
            ax[1].draw_artist(plot_points_right)
            fig.canvas.blit(ax[0].bbox)

            plt.pause(1/plot_sample_rate)
            # time.sleep(1/plot_sample_rate)
    except KeyboardInterrupt:
        raise_exception = True
        print("Interupted by user")
        playback_thread.join()
        sys.exit(1)

    # wait for the playback thread to finish
    playback_thread.join()

    print(len(data_array.get()))

    sys.exit(0)


def main(argv):

    data_array = AtomicArray(0)

    config = {
        'filename': '',
        'device': 0,
        'volume': 25000,
        'chunk': 1024,
        'duration': 0,
        'array': data_array        
    }

    try:
        opts, args = getopt.getopt(
            argv, "hi:d:v:", ["ifile=", "device=", "volume="])
    except getopt.GetoptError:
        print('wavPlayer.py -i <inputfile> -d <device_index> -v <volume>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('wavPlayer.py -i <inputfile> -d <device_index> -v <volume>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            config['filename'] = arg
        elif opt in ("-d", "--device"):
            config['device'] = int(arg)
        elif opt in ("-v", "--volume"):
            config['volume'] = int(arg)

    if config['filename'] == '':
        print('wavPlayer.py -i <inputfile> -d <device_index> -v <volume>')
        sys.exit(2)

    print('Input file is "', config['filename'])
    print('Device index is ', config['device'])

    run(config, data_array)

if __name__ == "__main__":
    main(sys.argv[1:])
