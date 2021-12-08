# MicroFinalProject

<h2>Libraries Needed:</h2>
<code>pi@raspberrypi:~ $ sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev</code>
<code>pi@raspberrypi:~ $ sudo pip3 install pyaudio</code>

<h2>Setup</h2>
<p>Running pyaudiotests.py will give a list of available audio devices. Theyre position in the list is the index. That needs to be passed to the input[output]_device_index parameter in both the pyaudio stream calls</p>

<h2>Useful Commands</h2>
<p>Lists audio devices for playback: <code>~ $ aplay -l</code></br>
Lists audio device names for playback <code>~ $ aplay -L</code></p>
</br>
<p>Lists audio devices for recording: <code>~ $ arecord -l</code></br>
Lists audio device names for recording <code>~ $ arecord -L</code></p>
</br>
<p>Plays audio file: <code>~ $ aplay -D [NAME] [FILE]</code></br>
ex: <code>~ $ aplay -D plughw:CARD=Headset,DEV=0 test1.wav</code></p>
