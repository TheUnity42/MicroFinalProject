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

extern const Config StdConfig = {44100, 1024, 1, 2, 0.0f};
extern const Config MonoConfig = {44100, 1024, 1, 1, 0.0f};

static int effectCallback(const void *inputBuffer, void *outputBuffer,
						  unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo *timeInfo,
						  PaStreamCallbackFlags statusFlags, void *userData) {

	ContextData *data = (ContextData *)userData;
	Config config = data->config;
	const SAMPLE *rptr = (const SAMPLE *)inputBuffer;
	SAMPLE *wptr = (SAMPLE *)outputBuffer;
	uint32_t i;
	uint16_t framesToCalc = config.FRAMES_PER_BUFFER;

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

    Buffer *buffer = new Buffer();
    buffer->input_buffer = (SAMPLE *)inputBuffer;
    buffer->output_buffer = (SAMPLE *)outputBuffer;
    buffer->input_buffer_size = framesPerBuffer * config.INPUT_CHANNELS * sizeof(SAMPLE);
    buffer->output_buffer_size = framesPerBuffer * config.OUTPUT_CHANNELS * sizeof(SAMPLE);
    buffer->framesProcessed = data->framesProcessed;
    buffer->timeInfo = *timeInfo;

	// process outside callback. If the callback returns false, we need to stop the stream
	if(!data->callback(buffer)) {
		return paComplete;
	}

	if(data->maxFramesToProcess == 0) {
        return paContinue;
    }
    data->framesProcessed += framesToCalc;
    if (data->framesProcessed >= data->maxFramesToProcess) {
        return paComplete;
    } else {
        return paContinue;
    }
}

void init(Container *container, ContextData context) {
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

void process(Container *container, ContextData context) {
    PaError err = Pa_StartStream(container->stream);
    if (err != paNoError) {
        throw EffectsException("Error starting PortAudio stream");
    }

    while (err = Pa_IsStreamActive(container->stream)) {
		Pa_Sleep(PROCESS_INTERVAL_DELAY);
	}

    if (err < 0) {
        throw EffectsException("Error Encountered in PortAudio stream");
    }
}

void consume(Container *container, ContextData context) {
	PaError err = Pa_CloseStream(container->stream);
    if (err != paNoError) {
        throw EffectsException("Error closing PortAudio stream");
    }

    err = Pa_Terminate();
    if (err != paNoError) {
        throw EffectsException("Error terminating PortAudio");
    }
}

} // namespace EffectsLib