# MicroFinalProject

<h2>Libraries Needed:</h2>
<code>pi@raspberrypi:~ $ sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev</code>
<code>pi@raspberrypi:~ $ sudo pip3 install pyaudio</code>

<h2>Setup</h2>
<p>Running pyaudiotests.py will give a list of available audio devices. Their position in the list is the index. That needs to be passed to the input[output]_device_index parameter in both the pyaudio stream calls</p>

<h2>Useful Commands</h2>
<p>Lists audio devices for playback: <code>~ $ aplay -l</code></br>
Lists audio device names for playback <code>~ $ aplay -L</code></p>
</br>
<p>Lists audio devices for recording: <code>~ $ arecord -l</code></br>
Lists audio device names for recording <code>~ $ arecord -L</code></p>
</br>
<p>Plays audio file: <code>~ $ aplay -D [NAME] [FILE]</code></br>
ex: <code>~ $ aplay -D plughw:CARD=Headset,DEV=0 test1.wav</code></p>

<h2>Numpy Stuff</h2>
Array Slicing:</br>
array[start:stop:step] is used to access multiple elements at once</br>
negative indexes start from the end of the array</br>
examples:
</br>
<code>
>>> a = np.array([1,2,3,4,5,6,7,8,9,10])</br>
>>> a[0] # takes the first element</br>
1</br>
>>> a[1:5] # takes the elements from index 1 to 4</br>
array([2, 3, 4, 5])</br>
>>> a[1:5:2] # takes the elements from index 1 to 4 with a step of 2</br>
array([2, 4])</br>
>>> a[::-1] # reverses the array (takes the elements from the start to the end with a step of -1, so it goes backwards)</br>
array([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])</br>
>>> a[::-2] # takes the elements from the start to the end with a step of -2, so it goes backwards and skips every other element</br>
array([10, 8, 6, 4, 2])</br>
>>> a[-1] # takes the last element</br>
10</br>
</code>
<br>
Slicing is MUTABLE:
<br>
<code>
>>> b = a[1:5] # sets b to be the elements from index 1 to 4</br>
>>> b[0] = 100 # changes the first element of b to be 100</br>
>>> a # a is also changed, as b is a reference to a</br>
array([1, 100, 3, 4, 5, 6, 7, 8, 9, 10])</br>
</code>