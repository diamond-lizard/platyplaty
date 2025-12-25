// audio_capture.cpp - PulseAudio capture implementation

#include "audio_capture.hpp"
#include "visualizer.hpp"
#include "shutdown.hpp"
#include "stderr_event.hpp"
#include <stdexcept>

namespace platyplaty {

AudioCapture::AudioCapture(const std::string& source, Visualizer& visualizer)
    : m_source(source), m_visualizer(visualizer) {
    m_mainloop = pa_threaded_mainloop_new();
    if (!m_mainloop) {
        throw std::runtime_error("Failed to create PulseAudio mainloop");
    }

    m_context = pa_context_new(
        pa_threaded_mainloop_get_api(m_mainloop), "platyplaty");
    if (!m_context) {
        pa_threaded_mainloop_free(m_mainloop);
        throw std::runtime_error("Failed to create PulseAudio context");
    }

    pa_context_set_state_callback(m_context, context_state_callback, this);
}

AudioCapture::~AudioCapture() {
    stop();
    join();
    if (m_stream) {
        pa_stream_disconnect(m_stream);
        pa_stream_unref(m_stream);
    }
    if (m_context) {
        pa_context_disconnect(m_context);
        pa_context_unref(m_context);
    }
    if (m_mainloop) {
        pa_threaded_mainloop_free(m_mainloop);
    }
}

void AudioCapture::context_state_callback(pa_context* ctx, void* userdata) {
    // The 'ctx' parameter is required by PulseAudio's callback signature
    // (pa_context_set_state_callback), but we don't need it here since we
    // access m_context through the userdata pointer. Without (void)ctx,
    // -Wunused-parameter warns. This silencing is safe because the parameter
    // is genuinely unused by design, not accidentally forgotten.
    (void)ctx;
    auto* self = static_cast<AudioCapture*>(userdata);
    pa_threaded_mainloop_signal(self->m_mainloop, 0);
}

void AudioCapture::stream_read_callback(pa_stream* stream, std::size_t, void* userdata) {
    // The 'stream' parameter is required by PulseAudio's callback signature
    // (pa_stream_set_read_callback), but we don't need it here since we
    // access m_stream through the userdata pointer. Without (void)stream,
    // -Wunused-parameter warns. This silencing is safe because the parameter
    // is genuinely unused by design, not accidentally forgotten.
    (void)stream;
    auto* self = static_cast<AudioCapture*>(userdata);
    pa_threaded_mainloop_signal(self->m_mainloop, 0);
}

void AudioCapture::wait_with_timeout() {
    pa_threaded_mainloop_wait(m_mainloop);
}

bool AudioCapture::read_and_submit_samples() {
    const void* data = nullptr;
    std::size_t nbytes = 0;
    int result = pa_stream_peek(m_stream, &data, &nbytes);
    while (result >= 0 && nbytes > 0) {
        if (data) {
            auto count = static_cast<unsigned int>(nbytes / (2 * sizeof(float)));
            m_visualizer.add_audio_samples(static_cast<const float*>(data), count);
        }
        pa_stream_drop(m_stream);
        result = pa_stream_peek(m_stream, &data, &nbytes);
    }
    return result >= 0;
}

void AudioCapture::capture_loop() {
    while (!m_stop_requested.load() && !g_shutdown_requested.load()) {
        pa_threaded_mainloop_lock(m_mainloop);
        wait_with_timeout();
        if (!read_and_submit_samples()) {
            pa_threaded_mainloop_unlock(m_mainloop);
            emit_stderr_event("AUDIO_ERROR", "Audio capture read failed");
            break;
        }
        pa_threaded_mainloop_unlock(m_mainloop);
    }
}

void AudioCapture::stop() {
    m_stop_requested.store(true);
}

void AudioCapture::join() {
    if (m_thread.joinable()) {
        m_thread.join();
    }
}

} // namespace platyplaty
