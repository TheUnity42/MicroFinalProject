from re import S
import pyaudio
import wave
import sys
import getopt


def play_audio(file, device_index, chucksize=1024):
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

    data = wf.readframes(chucksize)

    while len(data) > 0:
        print(data[0])
        stream.write(data)
        data = wf.readframes(chucksize)

    print("* done *")

    stream.stop_stream()
    stream.close()
    p.terminate()


def main(argv):
    file = ''
    device_index = 0
    try:
        opts, args = getopt.getopt(argv, "hi:d:", ["ifile=", "device="])
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

    if file == '':
        print('wavPlayer.py -i <inputfile> -d <device_index>')
        sys.exit(2)

    print('Input file is "', file)
    print('Device index is ', device_index)

    play_audio(file, device_index)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
