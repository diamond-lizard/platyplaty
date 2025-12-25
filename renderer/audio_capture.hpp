// audio_capture.hpp - PulseAudio capture for Platyplaty renderer
// RAII class that captures audio from PulseAudio and feeds to Visualizer.

#ifndef PLATYPLATY_AUDIO_CAPTURE_HPP
#define PLATYPLATY_AUDIO_CAPTURE_HPP

#include <pulse/pulseaudio.h>
#include <atomic>
#include <string>
#include <thread>

namespace platyplaty {

class Visualizer;  // Forward declaration

// RAII wrapper for PulseAudio audio capture.
// Captures audio from specified source and feeds samples to Visualizer.
class AudioCapture {
public:
    // Create capture for given source. Does not start capturing yet.
    AudioCapture(const std::string& source, Visualizer& visualizer);

    // Non-copyable
    AudioCapture(const AudioCapture&) = delete;
    AudioCapture& operator=(const AudioCapture&) = delete;

    // Non-movable
    AudioCapture(AudioCapture&&) = delete;
    AudioCapture& operator=(AudioCapture&&) = delete;

    // Cleanup PulseAudio resources
    ~AudioCapture();

    // Connect and start capturing. Throws on connection failure.
    void start();

    // Signal capture thread to stop
    void stop();

    // Wait for capture thread to finish
    void join();

private:
    void capture_loop();
    void wait_with_timeout();
    bool read_and_submit_samples();
    static void context_state_callback(pa_context* ctx, void* userdata);
    static void stream_read_callback(pa_stream* stream, std::size_t, void*);

    std::string m_source;
    Visualizer& m_visualizer;
    std::atomic<bool> m_stop_requested{false};
    std::thread m_thread;

    pa_threaded_mainloop* m_mainloop{nullptr};
    pa_context* m_context{nullptr};
    pa_stream* m_stream{nullptr};
};

} // namespace platyplaty

#endif // PLATYPLATY_AUDIO_CAPTURE_HPP
