/**
 * effectslib.cc
 *
 * Applies various effects to an audio stream.
 * Designed to be used as a plugin.
 *
 * Jared Talon Holton
 */

#include "include/effectslib.hh"
#include <math.h>
#include <portaudio.h>
#include <stdio.h>
#include <stdlib.h>

namespace EffectsLib {

static int effectCallback(const void *inputBuffer, void *outputBuffer,
						  unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo *timeInfo,
						  PaStreamCallbackFlags statusFlags, void *userData) {

	ContextData *data = (ContextData *)userData;
	Config config = data->config;
	const SAMPLE *rptr = (const SAMPLE *)inputBuffer;
	SAMPLE *wptr = (SAMPLE *)outputBuffer;
	long i;
	int framesToCalc = config.FRAMES_PER_BUFFER;

	(void)outputBuffer;
	(void)timeInfo;
	(void)statusFlags;
	(void)userData;

	if (inputBuffer == NULL) {
		for (i = 0; i < framesToCalc; i++) {
			*wptr++ = config.SAMPLE_SILENCE; /* left */
			if (config.OUTPUT_CHANNELS == 2)
				*wptr++ = config.SAMPLE_SILENCE; /* right */
		}
	} else {
		SAMPLE scratch;
		for (i = 0; i < framesToCalc; i++) {
			scratch = *rptr++;

			*wptr++ = scratch; /* left */
			if (config.OUTPUT_CHANNELS == 2)
				*wptr++ = scratch; /* right */
		}
	}

	return paContinue;
}

static void init(Container *container, ContextData context) {
	PaError err = paNoError;
	err = Pa_Initialize();
	if (err != paNoError) {
		throw EffectsException("Error initializing PortAudio");
	}

	container->inputParameters.device = Pa_GetDefaultInputDevice(); /* default input device */
	if (container->inputParameters.device == paNoDevice) {
		throw EffectsException("Error: No default input device.");
	}
	container->inputParameters.channelCount = context.config.INPUT_CHANNELS;
	container->inputParameters.sampleFormat = PA_SAMPLE_TYPE;
	container->inputParameters.suggestedLatency =
		Pa_GetDeviceInfo(container->inputParameters.device)->defaultLowInputLatency;
	container->inputParameters.hostApiSpecificStreamInfo = NULL;

	container->outputParameters.device = Pa_GetDefaultOutputDevice(); /* default output device */
	if (container->outputParameters.device == paNoDevice) {
		throw EffectsException("Error: No default output device.");
	}
	container->outputParameters.channelCount = context.config.OUTPUT_CHANNELS;
	container->outputParameters.sampleFormat = PA_SAMPLE_TYPE;
	container->outputParameters.suggestedLatency =
		Pa_GetDeviceInfo(container->outputParameters.device)->defaultLowOutputLatency;
	container->outputParameters.hostApiSpecificStreamInfo = NULL;

	err = Pa_OpenStream(&container->stream, &container->inputParameters,
						&container->outputParameters, context.config.SAMPLE_RATE,
						context.config.FRAMES_PER_BUFFER, paClipOff, effectCallback, &context);

    if (err != paNoError) {
        throw EffectsException("Error opening PortAudio stream");
    }
}

} // namespace EffectsLib