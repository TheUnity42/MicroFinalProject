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
#include "../resources/include/portaudio.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdexcept>
#include <functional>

#ifndef EFFECTSLIB_H
#define EFFECTSLIB_H

#define PA_SAMPLE_TYPE paFloat32
#define PROCESS_INTERVAL_DELAY 100


namespace EffectsLib {

typedef float SAMPLE;

typedef struct {
	uint16_t SAMPLE_RATE;
	uint16_t FRAMES_PER_BUFFER;
	uint8_t INPUT_CHANNELS;
	uint8_t OUTPUT_CHANNELS;
	SAMPLE SAMPLE_SILENCE;
} Config;

typedef struct {
	SAMPLE *input_buffer;
	SAMPLE *output_buffer;	
	uint32_t input_buffer_size;
	uint32_t output_buffer_size;
	uint32_t framesProcessed;
	PaStreamCallbackTimeInfo timeInfo;
} Buffer;

typedef struct {
	Config config;
    uint32_t framesProcessed;
    const uint32_t maxFramesToProcess;
    std::function<bool(Buffer*)> callback;
} ContextData;

typedef struct {
	PaStreamParameters inputParameters;
	PaStreamParameters outputParameters;
	PaStream *stream;	
} Container;

extern const Config StdConfig;
extern const Config MonoConfig;

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

/**
 * @brief Initializes and Opens the PortAudio stream
 *
 * @param container Container to initialize
 * @param context Context data for the stream
 */
void init(Container *container, ContextData context);

/**
 * @brief Starts audio processing and waits for completion
 * 
 * @param container Container holding stream data
 * @param context Context data for the stream
 */
void process(Container *container, ContextData context);

/**
 * @brief Closes the stream and terminates PortAudio
 * 
 * @param container Container holding stream data
 * @param context Context data for the stream
 */
void consume(Container *container, ContextData context);

class EffectsException : public std::runtime_error {
public:
    EffectsException() : std::runtime_error("no except"), code(0) {}
    EffectsException(const char* message) : std::runtime_error(message), code(255) {}
	EffectsException(const char* message, uint8_t code) : std::runtime_error(message), code(code) {}
	uint8_t which() const { return code; }
private:
uint8_t code;
};

} // namespace EffectsLib

#endif // EFFECTSLIB_H