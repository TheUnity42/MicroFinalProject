import pyaudio
import wave
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
help_str = "record.py - .wav file recorder\nUsage:\n\t-h\t\thelp\n\t-o\t<file>\toutput file name\n\t[-t]\t<sec>\tduration of recording (seconds) [default: 1]\n\t[-c]\t<num>\tNumber of channels [default: 1]"
options_dict = {
    'format': pyaudio.paInt32,
    'chans': 1,
    'sample_rate': 48000,
    'chunk_size': 4096,
    'record_secs': 1,
    'dev_index': 1,
    'filename': ""
}



def record(opt):
    audio = pyaudio.PyAudio()

    # create pyaudio stream object
    stream = audio.open(format=opt['format'], rate=opt['sample_rate'], channels=opt['chans'], input_device_index=opt['dev_index'], input=True, frames_per_buffer=opt['chunk_size'])

    print("Recording...")
    frames = []

    for i in range(0, (opt['sample_rate']//opt['chunk_size'])*opt['record_secs']):
        data = stream.read(opt['chunk_size'])        
        frames.append(data)
        
    print("Finished Recording.")

    # close resources
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save wav file
    wavefile = wave.open(opt['filename'], 'wb')
    wavefile.setnchannels(opt['chans'])
    wavefile.setsampwidth(audio.get_sample_size(opt['format']))
    wavefile.setframerate(opt['sample_rate'])
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ho:t:c:")
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

    if options_dict['filename'] == "":
        print("Must specify filename.")
        print(help_str)
        exit(1)

    print(f"Preparing to record {options_dict['record_secs']} seconds to {options_dict['filename']}...")

    record(options_dict)

if __name__ == '__main__':
    main(sys.argv[1:])