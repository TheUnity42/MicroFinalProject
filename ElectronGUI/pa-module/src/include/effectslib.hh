/**
 * effectslib.h
 *
 * Applies various effects to an audio stream.
 * Designed to be used as a plugin.
 *
 * Jared Talon Holton
 */

#include <cstdint>
#include <math.h>
#include <portaudio.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdexcept>

#ifndef EFFECTSLIB_H
#define EFFECTSLIB_H

#define PA_SAMPLE_TYPE paFloat32

namespace EffectsLib {

typedef float SAMPLE;

typedef struct {
	uint16_t SAMPLE_RATE;
	uint16_t FRAMES_PER_BUFFER;
	uint8_t INPUT_CHANNELS;
	uint8_t OUTPUT_CHANNELS;
	SAMPLE SAMPLE_SILENCE;
} Config;

extern const Config StdConfig = {44100, 1024, 1, 2, 0.0f};
extern const Config MonoConfig = {44100, 1024, 1, 1, 0.0f};

typedef struct {
	Config config;
} ContextData;

typedef struct {
	PaStreamParameters inputParameters;
	PaStreamParameters outputParameters;
	PaStream *stream;	
} Container;

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
						  PaStreamCallbackFlags statusFlags, void *userData);

static void init(Container *container, ContextData context);

class EffectsException : public std::runtime_error {
public:
    EffectsException(const char* message) : std::runtime_error(message) {}
};

} // namespace EffectsLib

#endif // EFFECTSLIB_H