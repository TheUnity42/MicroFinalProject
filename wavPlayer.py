import numpy as np
import pyaudio
import wave
import sys
import getopt
import matplotlib.pyplot as plt


def play_audio(file, device_index, volume, chunksize=4096):
    """ Play an audio file """
    wf = wave.open(file, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
        output_device_index=device_index
    )

    data = wf.readframes(chunksize)

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

    fig, ax = plt.subplots()
    ax.set_xlim(0, chunksize)
    ax.set_ylim(0, 1)
    # ax.set_aspect('equal')

    # stores the position of each sample (in frames)
    count = np.arange(0, chunksize)
    count_x = np.arange(0, chunksize)
    plot_points = ax.plot(count_x, fadefunc(count), 'b-')[0]
    
    plt.ion()
    plt.show()
    plt.pause(0.001)

    # cache background
    background = fig.canvas.copy_from_bbox(ax.bbox)

    while len(data) > 0:
        # read data from buffer into a mutable numpy array
        buffer = np.frombuffer(data, dtype=np.int16).copy()

        max_value = np.max(np.abs(buffer))
        if max_value > last_max:
            last_max = max_value

        buffer = buffer / last_max

        # isolates the left channel. [::2] will take every other element, starting at 0
        left = buffer[::2]
        # isolates the right channel. [1::2] will take every other element, starting at 1
        right = buffer[1::2]

        fade = fadefunc(count, 2)[:len(buffer) // 2]
        count += chunksize

        # multiply the left and right channels by the fade value
        # left[:] will modify the left channel in place, mutating the original buffer array
        # note the cast to np.int16, numpy really wants it to be a float32
        left[:] = (left[:] * fade)
        # right[:] will modify the right channel in place, mutating the original buffer array
        right[:] = (right[:] * (1-fade))

        # distort the output
        distort = exp_distort(buffer, 2)[:len(buffer)]
        buffer = buffer * distort

        buffer *= volume

        # buffer tobytes() will convert the now mutated buffer array back to a python bytes object
        # stream.write() will play the entire buffer (chunksize bytes)
        stream.write(buffer.astype(np.int16, copy=False).tobytes())

        # read the next chunk of data from the file
        data = wf.readframes(chunksize)        
        
        plot_points.set_data(np.arange(fade.shape[0]), fade)

        fig.canvas.restore_region(background)
        ax.draw_artist(plot_points)
        fig.canvas.blit(ax.bbox)

        plt.pause(0.0001)

    print("* done *")

    stream.stop_stream()
    stream.close()
    p.terminate()


def main(argv):
    file = ''
    device_index = 0
    volume = 25000
    try:
        opts, args = getopt.getopt(
            argv, "hi:d:v:", ["ifile=", "device=", "volume="])
    except getopt.GetoptError:
        print('wavPlayer.py -i <inputfile> -d <device_index>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('wavPlayer.py -i <inputfile> -d <device_index>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            file = arg
        elif opt in ("-d", "--device"):
            device_index = int(arg)
        elif opt in ("-v", "--volume"):
            volume = int(arg)

    if file == '':
        print('wavPlayer.py -i <inputfile> -d <device_index> -v <volume>')
        sys.exit(2)

    print('Input file is "', file)
    print('Device index is ', device_index)

    play_audio(file, device_index, volume)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
