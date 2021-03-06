/**
 * effects.c
 *
 * Applies various effect to an audio stream.
 * Effects include Fade, Delay, Reverb, and Clip Distort
 *
 * Jared Talon Holton
 * Rauly Baggett
 */
#include <portaudio.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

/** --- Sampling Config --- **/
#define SAMPLE_RATE 44100
#define FRAMES_PER_BUFFER 1024
#define NUM_CHANNELS 2

#define PA_SAMPLE_TYPE paFloat32
typedef float SAMPLE;
#define SAMPLE_SILENCE 0.0f
#define PRINTF_S_FORMAT "%.8f"

/** --- Reverb/Delay buffer --- **/
typedef struct {
	SAMPLE *buffer;
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
} EffectStates;

/** --- Global Variables --- **/
typedef struct {
	SAMPLE max;
	ReverbInfo reverb;
	ReverbInfo delay;
	EffectStates effects;
	float fade;
	float clip;
} paTestData;

/**
 * @brief Applies reverberation/delay to the audio sample  provided
 *
 * @param sample sample to be manipulated
 * @param info ReverbInfo struct containing the delay and reverb parameters
 */
static void reverbline(SAMPLE *sample, ReverbInfo *info);

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

			if (fabs(scratch) > max) {
				max = fabs(scratch);
			}

			scratch /= data->max;

			if (data->effects.reverb)
				reverbline(&scratch, &data->reverb);

			if (data->effects.delay)
				reverbline(&scratch, &data->delay);

			if (data->effects.distort)
				scratch *= data->clip;

			if (data->effects.fade) {
				*wptr++ = data->fade * scratch; /* left */
				if (NUM_CHANNELS == 2)
					*wptr++ = (1.0f - data->fade) * scratch; /* right */
			} else {
				*wptr++ = scratch; /* left */
				if (NUM_CHANNELS == 2)
					*wptr++ = scratch; /* right */
			}
		}
		if (max > data->max) {
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
	data.reverb.buffer = (SAMPLE *)malloc(maxReverb * sizeof(SAMPLE));
	for (int i = 0; i < maxReverb; i++) {
		data.reverb.buffer[i] = SAMPLE_SILENCE;
	}

	/* --- Delay Settings --- */
	data.delay.delayTime = maxDelay;
	data.delay.ptr = 0;
	data.delay.mixRate = 0.75;
	data.delay.holdRate = 0.0;
	data.delay.buffer = (SAMPLE *)malloc(maxDelay * sizeof(SAMPLE));
	for (int i = 0; i < maxDelay; i++) {
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
	err = Pa_OpenStream(&stream, &inputParameters, &outputParameters, SAMPLE_RATE,
						FRAMES_PER_BUFFER, paClipOff, effectCallback, &data);
	if (err != paNoError)
		goto done;

	err = Pa_StartStream(stream);
	if (err != paNoError)
		goto done;
	printf("\nPlaying!!\n");
	fflush(stdout);

	unsigned int num = 0;

	while ((err = Pa_IsStreamActive(stream)) == 1 && num < 5000) {
		Pa_Sleep(100);
		num++;
	}
	if (err < 0)
		goto done;

	err = Pa_CloseStream(stream);
	if (err != paNoError)
		goto done;

done:
	Pa_Terminate();

	/* --- Cleanup --- */
	if (data.reverb.buffer)
		free(data.reverb.buffer);
	if (data.delay.buffer)
		free(data.delay.buffer);

	if (err != paNoError) {
		fprintf(stderr, "An error occurred while using the portaudio stream\n");
		fprintf(stderr, "Error number: %d\n", err);
		fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
		err = 1; /* Always return 0 or 1, but no other return codes. */
	}
	return err;
}

static void reverbline(SAMPLE *sample, ReverbInfo *info) {
	SAMPLE y = info->buffer[info->ptr];
	info->buffer[info->ptr++] = *sample + (info->holdRate) * y;
	info->ptr = info->ptr % info->delayTime;
	if (info->holdRate)
		*sample = (1.0f - info->mixRate) * (*sample) + info->mixRate * y;
	else
		*sample += y;
}