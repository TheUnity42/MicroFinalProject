import numpy as np
import pyaudio
import wave
import sys
import getopt
import matplotlib.pyplot as plt
from matplotlib import widgets
import threading
import time
import logging

global raise_exception

global options
options = {
    "max_volume": 100000,
    "min_volume": 0,
    "default_volume": 30000,
}


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

class AtomicDict:
    def __init__(self, init_dict={}):
        self.dict = init_dict
        self._lock = threading.Lock()

    def set(self, key, value):
        with self._lock:
            self.dict[key] = value

    def get(self, key):
        with self._lock:
            return self.dict[key]
    
    def __getitem__(self, key):
        with self._lock:
            return self.dict[key]

    def __setitem__(self, key, value):
        with self._lock:
            self.dict[key] = value


def fadefunc(x, framerate, rate=2):
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
    return (np.sin(rate * x * np.pi / framerate) + 1) / 2


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


def play_audio(config: AtomicDict, raise_exception):
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

    last_max = 0

    # stores the position of each sample (in frames)
    count = np.arange(0, config['chunk'])

    
    M = int(config['effects']['delay_secs'] * wf.getframerate())
    D = np.zeros(M)
    ptr = 0

    def delayline(x, ptr):
        y = D[ptr]
        D[ptr] = x
        ptr = (ptr + 1) % M
        return y, ptr

    while len(data) > 0:
        # read effect values
        fade = config['effects']['fade']

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

        # multiply the left and right channels by the fade value
        if fade != 0.5:
            left = left * (1 - fade)
            right = right * fade
    
        # recombine the left and right channels
        buffer = np.empty((left.size + right.size,), dtype=right.dtype)
        buffer[0::2] = left
        buffer[1::2] = right

        # distort the output
        distort = exp_distort(buffer, 2)[:len(buffer)]
        buffer = buffer * distort

        config['array'].append(buffer)

        # add in old buffer

        if M > 0:
            for i in range(len(buffer)):
                v, ptr = delayline(buffer[i], ptr)
                buffer[i] += config['effects']['delay_amount'] * v

        buffer *= config['volume']

        # buffer tobytes() will convert the now mutated buffer array back to a python bytes object
        # stream.write() will play the entire buffer (chunksize bytes)
        stream.write(buffer.astype(np.int16, copy=False).tobytes())

        if raise_exception():
            raise Exception("InteruptException in playback thread")

        # read the next chunk of data from the file
        data = wf.readframes(config['chunk'])

    logging.info("* done *")

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
    global raise_exception
    raise_exception = False

    def handle_close_event(event):  # FIXME: why this no worky?
        global raise_exception
        raise_exception = True

    def raise_exception_func():
        global raise_exception
        return raise_exception

    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    fig.tight_layout(pad=3)

    plt.subplots_adjust(bottom=0.4)

    fig.canvas.mpl_connect('close_event', handle_close_event)

    playback_thread = threading.Thread(target=play_audio, args=(
        config, raise_exception_func), daemon=True)

    sliding_window_size = 48000*2
    window_subsample_rate = 128
    plot_sample_rate = 60

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

    plot_points_left = ax[0].plot(
        np.arange(sliding_window_size//2), np.zeros(sliding_window_size//2))[0]
    plot_points_right = ax[1].plot(
        np.arange(sliding_window_size//2), np.zeros(sliding_window_size//2))[0]


    vol_ax = plt.axes([0.10, 0.05, 0.32, 0.03])
    fader_ax = plt.axes([0.10, 0.10, 0.32, 0.03])
    vol_slider = widgets.Slider(vol_ax, 'Volume', valinit=config['volume'], valmin=options['min_volume'], valmax=options['max_volume'], valstep=1000)
    fader_slider = widgets.Slider(fader_ax, 'Fade Side', valinit=config['effects']['fade'], valmin=0, valmax=1, valstep=0.1)
    
    def update(effect):
        def update_func(val):
            config['effects'][effect] = val
            logging.info(f"Updated {effect} to {val}")
        return update_func

    fader_slider.on_changed(update('fade'))   
    vol_slider.on_changed(update('volume'))

    plt.ion()
    plt.show()
    plt.pause(0.1)

    time.sleep(0.5)
    playback_thread.start()

    # cache background
    background = fig.canvas.copy_from_bbox(ax[0].bbox)

    try:
        while playback_thread.is_alive():
            # update the data
            window_data = data_array.get()[-sliding_window_size:]

            window_data_left = subsample(window_data[::2], 2)

            plot_points_left.set_data(
                np.arange(window_data_left.shape[0]), window_data_left)

            window_data_right = subsample(
                window_data[-sliding_window_size+1::2], 2)

            plot_points_right.set_data(
                np.arange(window_data_right.shape[0]), window_data_right)

            # rebuild plot
            fig.canvas.restore_region(background)
            ax[0].draw_artist(plot_points_left)
            ax[1].draw_artist(plot_points_right)
            fig.canvas.blit(ax[0].bbox)

            plt.pause(1/plot_sample_rate)
            # time.sleep(1/plot_sample_rate)
    except KeyboardInterrupt:
        raise_exception = True
        logging.info("Interupted by user")
        playback_thread.join()
        sys.exit(1)

    # wait for the playback thread to finish
    playback_thread.join()

    logging.info(len(data_array.get()))


def main(argv):

    data_array = AtomicArray(0)

    config = {
        'filename': '',
        'device': 0,
        'volume': options['default_volume'],
        'chunk': 1024,
        'duration': 0,
        'array': data_array
    }
    config = AtomicDict(config)

    config['effects'] = AtomicDict()
    config['effects']['volume_roll_rate'] = 0.05
    config['effects']['fade'] = 0.5
    config['effects']['delay_secs'] = 0.1
    config['effects']['delay_amount'] = 0.5

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

    logging.info('Input file is "', config['filename'])
    logging.info('Device index is ', config['device'])

    run(config, data_array)
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main(sys.argv[1:])
