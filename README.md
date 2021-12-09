# MicroFinalProject

## Libraries Needed

```bash
pi@raspberrypi:~ $ sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
pi@raspberrypi:~ $ sudo pip3 install pyaudio
```

## Setup

Running pyaudiotests.py will give a list of available audio devices. Their position in the list is the index. That needs to be passed to the input[output]_device_index parameter in both the pyaudio stream calls

## Equations

$fft$

## Useful Commands

Lists audio devices for playback:

```bash
~ $ aplay -l
```

Lists audio device names for playback

```bash
~ $ aplay -L
```

Lists audio devices for recording:

```bash
~ $ arecord -l
```

Lists audio device names for recording

```bash
~ $ arecord -L
```

Plays audio file:

```bash
~ $ aplay -D [NAME] [FILE]</code>
```

ex:

```bash
~ $ aplay -D plughw:CARD=Headset,DEV=0 test1.wav</code></p>
```

## Numpy Stuff

Array Slicing:
array[start:stop:step] is used to access multiple elements at once
negative indexes start from the end of the array
examples:

```python
>>> a = np.array([1,2,3,4,5,6,7,8,9,10])
>>> a[0] # takes the first element
1
>>> a[1:5] # takes the elements from index 1 to 4
array([2, 3, 4, 5])
>>> a[1:5:2] # takes the elements from index 1 to 4 with a step of 2
array([2, 4])
>>> a[::-1] # reverses the array (takes the elements from the start to the end with a step of -1, so it goes backwards)
array([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
>>> a[::-2] # takes the elements from the start to the end with a step of -2, so it goes backwards and skips every other element
array([10, 8, 6, 4, 2])
>>> a[-1] # takes the last element
10
```

Slicing is MUTABLE:

```python
>>> b = a[1:5] # sets b to be the elements from index 1 to 4
>>> b[0] = 100 # changes the first element of b to be 100
>>> a # a is also changed, as b is a reference to a
array([1, 100, 3, 4, 5, 6, 7, 8, 9, 10])
```
