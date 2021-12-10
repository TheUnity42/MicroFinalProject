import pyaudio
import wave
import numpy as np
import sys, getopt

# dict config: {
# form: pyaudio.paInt32
# chans: 
# sample_rate:
# chunk_size: 
# record_secs: 
# dev_index: 
# 
# }
help_str = "record.py - .wav file recorder\nUsage:\n\t-h\t\thelp\n\t-o\t<file>\toutput file name\n\t[-t]\t<sec>\tduration of recording (seconds) [default: 1]\n\t[-c]\t<num>\tNumber of channels [default: 1]\n\t[-d]\t<index>\tDevice Index [default: 0]"
options_dict = {
    'format': pyaudio.paInt32,
    'chans': 1,
    'sample_rate': 16000,
    'chunk_size': 1024,
    'record_secs': 1,
    'dev_index': 0,
    'filename': ""
}



def record(opt, audio):    

    # create pyaudio stream object
    stream = audio.open(format=opt['format'], rate=opt['sample_rate'], channels=opt['chans'], input_device_index=opt['dev_index'], input=True, frames_per_buffer=opt['chunk_size'])

    frames = []

    for i in range(0, (opt['sample_rate']//opt['chunk_size'])*opt['record_secs']):
        data = stream.read(opt['chunk_size'])
        # np_arr = np.frombuffer(data, dtype=np.int16)
        # np_arr = np.repeat(np_arr, 2)
        # frames.append(np_arr.astype(np.int16).tobytes())
        frames.append(data)
        
    print("Finished Recording.")

    # close resources
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save wav file
    wavefile = wave.open(opt['filename'], 'wb')
    wavefile.setnchannels(1)
    wavefile.setsampwidth(audio.get_sample_size(opt['format']))
    wavefile.setframerate(opt['sample_rate'])
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ho:t:c:d:")
    except getopt.GetoptError:
        print(help_str)
        exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(help_str)
            exit(0)
        elif opt == '-o':
            options_dict['filename'] = arg
        elif opt == '-t':
            options_dict['record_secs'] = int(arg)
        elif opt == '-c':
            options_dict['chans'] = arg
        elif opt == '-d':
            options_dict['dev_index'] = int(arg)

    if options_dict['filename'] == "":
        print("Must specify filename.")
        print(help_str)
        exit(1)

    audio = pyaudio.PyAudio()

    print('\n', f"Recording {options_dict['record_secs']} seconds to {options_dict['filename']}...", sep='')

    record(options_dict, audio)

if __name__ == '__main__':
    main(sys.argv[1:])
