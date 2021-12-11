"""
    statsplay.py - Interactive plotting and effects program
    Jared Talon Holton
    Rauly Baggett
"""

import getopt
import logging
import sys
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from matplotlib import widgets

global raise_exception

global options
options = {
    "max_volume": 2**15,
    "min_volume": 0,
    "default_volume": 10000,
    "framerate": 44100,
    "channels": 2,
    "input_channels": 1,
    "format": pyaudio.paInt16,
    "filter": "equiripple56.mat",
    "filter_type": "equiripple",
    "filter_order": 56,
    "filter_coef": 0,
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

    def remove(self, value):
        with self._lock:
            self.array = np.delete(self.array, value)


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


def tanh_distort(v, ratio=0.5):
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
    return np.tanh(v) * ratio * np.sin(v)


def clip_distort(v, ratio):
    """
    Clips values to a maximum
    """
    return np.where(np.abs(ratio * v) > 1, 1, v * ratio)


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

    framerate = options['framerate']

    p = pyaudio.PyAudio()

    stream = p.open(
        format=options['format'],
        channels=options['channels'],
        rate=options['framerate'],
        output=True,
        output_device_index=config['device']
    )

    in_stream = p.open(
        format=options['format'],
        channels=options['input_channels'],
        rate=options['framerate'],
        input=True,
        output_device_index=config['input']
    )

    data = in_stream.read(config['chunk'])

    last_max = options['default_volume']

    M = int(config['effects']['delay_secs'] * options['framerate'])
    D = np.zeros(5 * options['framerate'])
    ptr = 0

    def delayline(x, ptr):
        y = D[ptr]
        D[ptr] = x
        ptr = (ptr + 1) % M
        return y, ptr

    Mr = int(config['effects']['reverb_secs'] * options['framerate'])
    R = np.zeros(5 * options['framerate'])
    ptrr = 0

    def reverbline(x, ptr):
        y = R[ptr]
        R[ptr] = x + config['effects']['reverb_falloff']*y
        ptr = (ptr + 1) % Mr
        return y, ptr

    # Mf = int(framerate * (80/1000)) # max delay
    # Mfmin = int(framerate * (40/1000)) # min delay
    # F = np.zeros(Mf)
    # Fptr = 0
    # Fmod = Mf//2
    # fCount = 0

    # def flangeline(x, ptr, m):
    #     y = F[ptr]
    #     F[ptr] = x
    #     ptr = (ptr + 1) % m
    #     return y, ptr

    # for i in range(config['num_chunks']):
    while 1:
        # read effect values
        # helps prevent thread collisions if read only once
        fade = config['effects']['fade']
        volume = config['volume']
        clip_distort_v = config['effects']['clip_distort']

        M = int(config['effects']['delay_secs'] * options['framerate'])

        # read data from buffer into a mutable numpy array
        inputs = np.frombuffer(data, dtype=np.int16)

        max_value = np.max(np.abs(inputs))
        if max_value > last_max:
            last_max = max_value
        else:
            last_max = (last_max * (1 - config['effects']['volume_roll_rate'])) + (
                max_value * config['effects']['volume_roll_rate'])

        inputs = inputs / last_max

        config['input_array'].append(inputs)

        buffer = inputs.copy()

        # distort the output
        if clip_distort_v > 0:
            buffer = clip_distort(buffer, clip_distort_v)

        if M > 0:
            for i in range(len(buffer)):
                v, ptr = delayline(buffer[i], ptr)
                buffer[i] += config['effects']['delay_amplitude'] * v + \
                    (1 - config['effects']['delay_amplitude']) * buffer[i]

        if Mr > 0:
            for i in range(len(buffer)):
                v, ptrr = reverbline(buffer[i], ptrr)
                buffer[i] += config['effects']['reverb_amplitude'] * v + \
                    (1 - config['effects']['reverb_amplitude']) * buffer[i]

        buffer = np.repeat(buffer, 2).copy()

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

        config['array'].append(buffer)

        buffer *= volume
        # buffer tobytes() will convert the now mutated buffer array back to a python bytes object
        # stream.write() will play the entire buffer (chunksize bytes)
        stream.write(buffer.astype(np.int16, copy=False).tobytes())

        if raise_exception():
            raise Exception("InteruptException in playback thread")

        # read the next chunk of data from the file
        data = in_stream.read(config['chunk'])

    logging.info("* done *")

    stream.stop_stream()
    stream.close()
    in_stream.stop_stream()
    in_stream.close()
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


def run(config, data_array, input_array):
    global raise_exception
    raise_exception = False

    def handle_close_event(event):
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

    sliding_window_size = 48000
    window_subsample_rate = 16
    plot_sample_rate = 60

    ax[1].set_xlabel('Frames')
    ax[1].set_ylabel('Amplitude')
    ax[1].set_title('Output Signal')
    ax[1].set_ylim([-2, 2])
    ax[1].set_xlim([0, sliding_window_size//(2*window_subsample_rate)])

    ax[0].set_xlabel('Frames')
    ax[0].set_ylabel('Amplitude')
    ax[0].set_title('Input Signal')
    ax[0].set_ylim([-1, 1])
    ax[0].set_xlim([0, sliding_window_size//(2*window_subsample_rate)])

    plot_points_left = ax[1].plot(
        np.arange(sliding_window_size//2), np.zeros(sliding_window_size//2), c='b', label='Left')[0]
    plot_points_right = ax[1].plot(
        np.arange(sliding_window_size//2), np.zeros(sliding_window_size//2), c='r', label='Right')[0]
    ax[1].legend()

    plot_points_input = ax[0].plot(np.arange(
        sliding_window_size//2), np.zeros(sliding_window_size//2), c='g', label='Input')[0]

    vol_ax = plt.axes([0.11, 0.05, 0.30, 0.03])
    fader_ax = plt.axes([0.11, 0.10, 0.30, 0.03])
    clip_distort_ax = plt.axes([0.11, 0.15, 0.32, 0.03])
    delay_ax = plt.axes([0.60, 0.20, 0.30, 0.03])
    delay_amplitude_ax = plt.axes([0.60, 0.15, 0.30, 0.03])
    reverb_ax = plt.axes([0.60, 0.10, 0.30, 0.03])
    reverb_amplitude_ax = plt.axes([0.60, 0.05, 0.30, 0.03])

    vol_slider = widgets.Slider(
        vol_ax, 'Volume', valinit=config['volume'], valmin=options['min_volume'], valmax=options['max_volume'], valstep=1000)
    fader_slider = widgets.Slider(
        fader_ax, 'Fade Side', valinit=config['effects']['fade'], valmin=0, valmax=1, valstep=0.1)
    clip_distort_slider = widgets.Slider(
        clip_distort_ax, 'Clip Distort', valinit=config['effects']['clip_distort'], valmin=0, valmax=10)
    delay_slider = widgets.Slider(
        delay_ax, 'Delay', valinit=config['effects']['delay_secs'], valmin=0, valmax=5, valstep=0.1)
    delay_amp_slider = widgets.Slider(
        delay_amplitude_ax, 'Delay Amp', valinit=config['effects']['delay_amplitude'], valmin=0, valmax=1, valstep=0.1)

    reverb_slider = widgets.Slider(
        reverb_ax, 'Reverb', valinit=config['effects']['reverb_secs'], valmin=0, valmax=2, valstep=0.05)
    reverb_amp_slider = widgets.Slider(
        reverb_amplitude_ax, 'Reverb Falloff', valinit=config['effects']['reverb_falloff'], valmin=0, valmax=1)

    def update(effect, is_effect=True):
        def update_func(val):
            if is_effect:
                config['effects'][effect] = val
            else:
                config[effect] = val
            logging.info(f"Updated {effect} to {val}")
        return update_func

    fader_slider.on_changed(update('fade'))
    clip_distort_slider.on_changed(update('clip_distort'))
    delay_slider.on_changed(update('delay_secs'))
    delay_amp_slider.on_changed(update('delay_amplitude'))
    reverb_slider.on_changed(update('reverb_secs'))
    reverb_amp_slider.on_changed(update('reverb_falloff'))
    vol_slider.on_changed(update('volume', False))

    plt.ion()
    plt.show()
    plt.pause(0.1)

    data_array.append(np.zeros(sliding_window_size))

    time.sleep(0.5)
    playback_thread.start()

    # cache background
    background = fig.canvas.copy_from_bbox(ax[0].bbox)

    fft_max = 0

    try:
        while playback_thread.is_alive():
            # update the data
            all_data = data_array.get()
            window_data = all_data[-sliding_window_size:]

            window_data_left = subsample(
                window_data[::2], window_subsample_rate)

            window_data_right = subsample(
                window_data[1::2], window_subsample_rate)

            # amplitude plots
            plot_points_left.set_data(
                np.arange(window_data_left.shape[0]), window_data_left+1)

            plot_points_right.set_data(
                np.arange(window_data_right.shape[0]), window_data_right-1)

            # update input data
            in_data = input_array.get()
            window_in_data = in_data[-sliding_window_size:]
            window_in_data = subsample(window_in_data, window_subsample_rate)

            plot_points_input.set_data(
                np.arange(window_in_data.shape[0]), window_in_data)

            # shorten data arrays
            if in_data.shape[0] > sliding_window_size * 2:
                data_array.remove(np.s_[:sliding_window_size])
                input_array.remove(np.s_[:sliding_window_size])

            # rebuild plot
            fig.canvas.restore_region(background)
            ax[1].draw_artist(plot_points_left)
            ax[1].draw_artist(plot_points_right)
            ax[0].draw_artist(plot_points_input)
            fig.canvas.blit(ax[0].bbox)

            # plt.pause(1/plot_sample_rate)
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
    input_array = AtomicArray(0)

    config = {
        'filename': '',
        'device': 0,
        'input': 0,
        'volume': options['default_volume'],
        'chunk': 1024,
        'frame_rate': 44100,
        'duration': 0,
        'array': data_array,
        'input_array': input_array,
    }
    config = AtomicDict(config)

    config['effects'] = AtomicDict()
    config['effects']['volume_roll_rate'] = 0.0001
    config['effects']['fade'] = 0.5
    config['effects']['delay_secs'] = 0
    config['effects']['delay_amplitude'] = 0.5

    config['effects']['clip_distort'] = 0.0
    config['effects']['reverb_secs'] = 0.5
    config['effects']['reverb_falloff'] = 0.5
    config['effects']['reverb_amplitude'] = 0.5

    try:
        opts, args = getopt.getopt(
            argv, "hi:d:v:f:", ["file=", "device=", "volume=", "input="])
    except getopt.GetoptError:
        print('statsplay.py -f <inputfile> -d <device_index> -i <input_index> -v <volume>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'statsplay.py -f <inputfile> -d <device_index> -i <input_index> -v <volume>')
            sys.exit()
        elif opt in ("-f", "--file"):
            config['filename'] = arg
        elif opt in ("-d", "--device"):
            config['device'] = int(arg)
        elif opt in ("-i", "--input"):
            config['input'] = int(arg)
        elif opt in ("-v", "--volume"):
            config['volume'] = int(arg)

    if config['input'] == 0:
        print('statsplay.py -f <inputfile> -d <device_index> -i <input_index> -v <volume>')
        print("\nNo input selected -- Using default")

    print('Input index is ', config['input'])
    print('Device index is ', config['device'])

    run(config, data_array, input_array)
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main(sys.argv[1:])
