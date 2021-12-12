/**
 * pi_effects.c 
 * 
 * Applies various effect to an audio stream on a raspberry pi.
 * Effects include Fade, Delay, Reverb, and Clip Distort
 * Includes wiring pi configuration for controlling effects externally
 *
 * Jared Talon Holton
 * Rauly Baggett
 */
#include "portaudio.h"
#include "wiringPi.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/** --- Sampling Config --- **/
#define SAMPLE_RATE 44100
#define FRAMES_PER_BUFFER 1024
#define NUM_CHANNELS 2

#define PA_SAMPLE_TYPE paFloat32
typedef float SAMPLE;
#define SAMPLE_SILENCE 0.0f
#define PRINTF_S_FORMAT "%.8f"

/** --- Input pin config --- **/
#define FADE_PIN 0
#define DELAY_PIN 1
#define REVERB_PIN 2
#define DISTORT_PIN 3
#define INC_PIN 4
#define DEC_PIN 5

/** --- Reverb/Delay buffer --- **/
typedef struct {
	SAMPLE* buffer;
	unsigned int ptr;
	unsigned int delayTime;
	float mixRate;
	float holdRate;
} ReverbInfo;

/** --- Pin States --- **/
typedef struct {
	short fade;
	short delay;
	short reverb;
	short distort;
	short inc;
	short dec;
} PinInfo;

/** --- Global Variables --- **/
typedef struct {
	SAMPLE max;
	ReverbInfo reverb;
	ReverbInfo delay;
	PinInfo pins;
	float fade;
	float clip;
} paTestData;

/**
 * @brief Applies reverberation/delay to the audio sample  provided
 * 
 * @param sample sample to be manipulated
 * @param info ReverbInfo struct containing the delay and reverb parameters
 */
static void reverbline(SAMPLE* sample, ReverbInfo* info);

/**
 * @brief Polls the input pins and sets the corresponding PinInfo information
 * 
 * @param pins PinInfo struct containing the current state of the input pins
 */
static void pollPins(PinInfo* pins);

/**
 * @brief Callback for PortAudio. Processes the input stream and applies effects
 * 
 * @param inputBuffer input buffer for recording device
 * @param outputBuffer output buffer for playback device
 * @param framesPerBuffer samples in each buffer
 * @param timeInfo time info from PortAudio
 * @param statusFlags status info from PortAudio
 * @param userData global data for the callback
 * @return int Status code from PortAudio
 */
static int effectCallback(const void *inputBuffer, void *outputBuffer,
						  unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo *timeInfo,
						  PaStreamCallbackFlags statusFlags, void *userData) {
	paTestData *data = (paTestData *)userData;
	const SAMPLE *rptr = (const SAMPLE *)inputBuffer;
	SAMPLE *wptr = (SAMPLE *)outputBuffer;
	long i;
	int finished;
	int framesToCalc = FRAMES_PER_BUFFER;

	(void)outputBuffer;
	(void)timeInfo;
	(void)statusFlags;
	(void)userData;

	if (inputBuffer == NULL) {
		for (i = 0; i < framesToCalc; i++) {
			*wptr++ = SAMPLE_SILENCE; /* left */
			if (NUM_CHANNELS == 2)
				*wptr++ = SAMPLE_SILENCE; /* right */
		}
	} else {
		SAMPLE scratch;
		SAMPLE max = data->max;
		for (i = 0; i < framesToCalc; i++) {
			scratch = *rptr++;

			if(fabs(scratch) > max) {
				max = fabs(scratch);
			}

			scratch /= data->max;

			if(data->pins.reverb)
				reverbline(&scratch, &data->reverb);

			if(data->pins.delay)
				reverbline(&scratch, &data->delay);

			if(data->pins.distort)
				scratch *= data->clip;

			if(data->pins.fade) {
				*wptr++ = data->fade * scratch; /* left */
				if (NUM_CHANNELS == 2)
					*wptr++ = (1.0f - data->fade) * scratch; /* right */
			} else {
				*wptr++ = scratch; /* left */
				if (NUM_CHANNELS == 2)
					*wptr++ = scratch; /* right */
			}
		}		
		if(max > data->max) {
			data->max = max;
		} else {
			data->max = 0.999 * data->max;
		}
	}

	finished = paContinue;
	return finished;
}

int main(void) {
	PaStreamParameters inputParameters, outputParameters;
	PaStream *stream;
	PaStream *out_stream;
	PaError err = paNoError;
	paTestData data;
	int totalFrames;
	int numSamples;
	int numBytes;
	int maxReverb;
	int maxDelay;

	if(wiringPiSetup() == -1){ /*when initialize wiring failed, print message to screen*/
    	printf("setup wiringPi failed!");
    	return 1;
  	}

	/* --- Initialize Pin States --- */
	pinMode(FADE_PIN, INPUT);
	pinMode(DELAY_PIN, INPUT);
	pinMode(REVERB_PIN, INPUT);
	pinMode(DISTORT_PIN, INPUT);

	numSamples = totalFrames * NUM_CHANNELS;
	numBytes = numSamples * sizeof(SAMPLE);

	maxReverb = SAMPLE_RATE;
	maxDelay = 3 * SAMPLE_RATE;

	/* --- General Settings --- */
	data.max = 0.5;
	data.fade = 0.0;
	data.clip = 10;

	/* --- Reverb Settings --- */
	data.reverb.delayTime = maxReverb;
	data.reverb.ptr = 0;
	data.reverb.mixRate = 0.25;
	data.reverb.holdRate = 0.5;
	data.reverb.buffer = (SAMPLE*) malloc(maxReverb * sizeof(SAMPLE));
	for(int i = 0; i < maxReverb; i++) {
		data.reverb.buffer[i] = SAMPLE_SILENCE;
	}

	/* --- Delay Settings --- */
	data.delay.delayTime = maxDelay;
	data.delay.ptr = 0;
	data.delay.mixRate = 0.75;
	data.delay.holdRate = 0.0;
	data.delay.buffer = (SAMPLE*) malloc(maxDelay * sizeof(SAMPLE));
	for(int i = 0; i < maxDelay; i++) {
		data.delay.buffer[i] = SAMPLE_SILENCE;
	}

	/* --- init PortAudio --- */
	err = Pa_Initialize();
	if (err != paNoError)
		goto done;

	inputParameters.device = Pa_GetDefaultInputDevice(); /* default input device */
	if (inputParameters.device == paNoDevice) {
		fprintf(stderr, "Error: No default input device.\n");
		goto done;
	}
	inputParameters.channelCount = 1; /* non stereo input */
	inputParameters.sampleFormat = PA_SAMPLE_TYPE;
	inputParameters.suggestedLatency =
		Pa_GetDeviceInfo(inputParameters.device)->defaultLowInputLatency;
	inputParameters.hostApiSpecificStreamInfo = NULL;

	outputParameters.device = Pa_GetDefaultOutputDevice(); /* default output device */
	if (outputParameters.device == paNoDevice) {
		fprintf(stderr, "Error: No default output device.\n");
		goto done;
	}
	outputParameters.channelCount = 2; /* stereo output */
	outputParameters.sampleFormat = PA_SAMPLE_TYPE;
	outputParameters.suggestedLatency =
		Pa_GetDeviceInfo(outputParameters.device)->defaultLowOutputLatency;
	outputParameters.hostApiSpecificStreamInfo = NULL;

	/* Apply effects -------------------------------------------- */
	err = Pa_OpenStream(
		&stream, &inputParameters, &outputParameters,
		SAMPLE_RATE, FRAMES_PER_BUFFER,
		paClipOff,
		effectCallback,
		 &data);
	if (err != paNoError)
		goto done;

	err = Pa_StartStream(stream);
	if (err != paNoError)
		goto done;
	printf("\nPlaying!!\n");

	unsigned int num = 0;

	while ((err = Pa_IsStreamActive(stream)) == 1 && num < 5000) {
		Pa_Sleep(100);
		
		num++;
		pollPins(&data.pins);

		/* --- Handle Changing Effect Values --- */

		if(data.pins.fade) {
			if(data.pins.inc) {
				data.fade += 0.1;
				if (data.fade > 1) {
					data.fade = 0;
				}
			} else if (data.pins.dec) {
				data.fade -= 0.1;
				if (data.fade < 0) {
					data.fade = 1;
				}
			}
		}

		if(data.pins.delay) {
			if(data.pins.inc) {
				data.delay.delayTime *= 1.1;
				if (data.delay.delayTime > maxDelay) {
					data.delay.delayTime = 100;
				}
			} else if (data.pins.dec) {
				data.delay.delayTime *= 0.9;
				if (data.delay.delayTime < 100) {
					data.delay.delayTime = maxDelay;
				}
			}
		}

		if(data.pins.reverb) {
			if(data.pins.inc) {
				data.reverb.delayTime *= 1.1;
				if (data.reverb.delayTime > maxReverb) {
					data.reverb.delayTime = 10;
				}
			} else if (data.pins.dec) {
				data.reverb.delayTime *= 0.9;
				if (data.reverb.delayTime < 10) {
					data.reverb.delayTime = maxReverb;
				}
			}
		}

		if(data.pins.distort) {
			if(data.pins.inc) {
				data.clip += 1;
				if (data.clip > 20) {
					data.clip = 1;
				}
			} else if (data.pins.dec) {
				data.clip -= 1;
				if (data.clip < 1) {
					data.clip = 1;
				}
			}
		}		
	}
	if (err < 0)
		goto done;

	err = Pa_CloseStream(stream);
	if (err != paNoError)
		goto done;

done:
	Pa_Terminate();

	/* --- Cleanup --- */
	if(data.reverb.buffer)
		free(data.reverb.buffer);
	if(data.delay.buffer)
		free(data.delay.buffer);
	
	if (err != paNoError) {
		fprintf(stderr, "An error occurred while using the portaudio stream\n");
		fprintf(stderr, "Error number: %d\n", err);
		fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
		err = 1; /* Always return 0 or 1, but no other return codes. */
	}
	return err;
}

static void pollPins(PinInfo* pins) {
	pins->fade = digitalRead(FADE_PIN);
	pins->delay = digitalRead(DELAY_PIN);	
	pins->reverb = digitalRead(REVERB_PIN);
	pins->distort = digitalRead(DISTORT_PIN);
	pins->inc = digitalRead(INC_PIN);
	pins->dec = digitalRead(DEC_PIN);
}

static void reverbline(SAMPLE* sample, ReverbInfo* info) {
	SAMPLE y = info->buffer[info->ptr];
	info->buffer[info->ptr++] = *sample + (info->holdRate) * y;
	info->ptr = info->ptr % info->delayTime;
	if(info->holdRate)
		*sample = (1.0f - info->mixRate) * (*sample) + info->mixRate * y;
	else
		*sample += y;
}