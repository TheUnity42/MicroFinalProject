# MicroFinalProject

## Libraries Needed

```bash
pi@raspberrypi:~ $ sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
pi@raspberrypi:~ $ sudo pip3 install pyaudio
```

## Setup

Running pyaudiotests.py will give a list of available audio devices. Their position in the list is the index. That needs to be passed to the input[output]_device_index parameter in both the pyaudio stream calls

C code will use the default input and output device.
