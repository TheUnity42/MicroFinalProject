import numpy as np
import pyaudio
import wave
import sys
import getopt
import time


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

    count = 0
    t = time.time()

    while len(data) > 0:
        # read data from buffer into a mutable numpy array
        buffer = np.frombuffer(data, dtype=np.int16).copy()

        # isolates the left channel. [::2] will take every other element, starting at 0
        left = buffer[::2]
        # isolates the right channel. [1::2] will take every other element, starting at 1
        right = buffer[1::2]

        # using the current time, calulate a fade value between 0, 1
        fade = (np.sin((time.time() - t) * np.pi / 2) + 1) / 2

        # multiply the left and right channels by the fade value
        # left[:] will modify the left channel in place, mutating the original buffer array
        # note the cast to np.int16, numpy really wants it to be a float32
        left[:] = (left[:] * fade).astype(np.int16, copy=False)
        # right[:] will modify the right channel in place, mutating the original buffer array
        right[:] = (right[:] * (1-fade)).astype(np.int16, copy=False)

        # buffer tobytes() will convert the now mutated buffer array back to a python bytes object
        # stream.write() will play the entire buffer (chunksize bytes)
        stream.write(buffer.tobytes())

        # read the next chunk of data from the file
        data = wf.readframes(chunksize)

    print("* done *")

    stream.stop_stream()
    stream.close()
    p.terminate()


def main(argv):
    file = ''
    device_index = 0
    volume = 5000
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
