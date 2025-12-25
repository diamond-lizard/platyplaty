// audio_capture_start.cpp - PulseAudio stream initialization

#include "audio_capture.hpp"
#include <stdexcept>

namespace platyplaty {

void AudioCapture::start() {
    pa_threaded_mainloop_start(m_mainloop);
    pa_threaded_mainloop_lock(m_mainloop);

    pa_context_connect(m_context, nullptr, PA_CONTEXT_NOFLAGS, nullptr);

    // Wait for context to be ready
    while (true) {
        auto state = pa_context_get_state(m_context);
        if (state == PA_CONTEXT_READY) {
            break;
        }
        if (!PA_CONTEXT_IS_GOOD(state)) {
            pa_threaded_mainloop_unlock(m_mainloop);
            throw std::runtime_error("PulseAudio context connection failed");
        }
        pa_threaded_mainloop_wait(m_mainloop);
    }

    // Create stream with 44100Hz stereo float32
    pa_sample_spec spec{};
    spec.format = PA_SAMPLE_FLOAT32LE;
    spec.rate = 44100;
    spec.channels = 2;

    m_stream = pa_stream_new(m_context, "platyplaty-capture", &spec, nullptr);
    if (!m_stream) {
        pa_threaded_mainloop_unlock(m_mainloop);
        throw std::runtime_error("Failed to create PulseAudio stream");
    }

    pa_stream_set_read_callback(m_stream, stream_read_callback, this);

    // Buffer for ~735 samples (~16.7ms at 44100Hz)
    pa_buffer_attr attr{};
    attr.maxlength = static_cast<uint32_t>(-1);
    attr.fragsize = 735 * 2 * sizeof(float);  // stereo float32

    int result = pa_stream_connect_record(
        m_stream, m_source.c_str(), &attr, PA_STREAM_ADJUST_LATENCY);
    if (result < 0) {
        pa_threaded_mainloop_unlock(m_mainloop);
        throw std::runtime_error("Failed to connect PulseAudio stream");
    }

    // Wait for stream to be ready
    while (true) {
        auto state = pa_stream_get_state(m_stream);
        if (state == PA_STREAM_READY) {
            break;
        }
        if (!PA_STREAM_IS_GOOD(state)) {
            pa_threaded_mainloop_unlock(m_mainloop);
            throw std::runtime_error("PulseAudio stream connection failed");
        }
        pa_threaded_mainloop_wait(m_mainloop);
    }

    pa_threaded_mainloop_unlock(m_mainloop);

    m_thread = std::thread(&AudioCapture::capture_loop, this);
}

} // namespace platyplaty
