// Netstring parsing and serialization implementation.

#include "netstring.hpp"
#include <numeric>

namespace platyplaty {

namespace {

bool is_digit(char c) {
    return c >= '0' && c <= '9';
}

}  // namespace

NetstringParseResult parse_netstring(
    const std::string& input,
    std::size_t& bytes_consumed) {

    bytes_consumed = 0;

    if (input.empty()) {
        return {false, "", "incomplete: empty input"};
    }

    // Find the colon separator
    std::size_t colon_pos = 0;
    while (colon_pos < input.size() && is_digit(input[colon_pos])) {
        ++colon_pos;
    }

    // Validate length prefix
    if (colon_pos == 0) {
        return {false, "", "invalid: length prefix missing"};
    }
    if (colon_pos > MAX_LENGTH_DIGITS) {
        return {false, "", "invalid: length prefix too long"};
    }
    if (colon_pos >= input.size()) {
        return {false, "", "incomplete: waiting for colon"};
    }
    if (input[colon_pos] != ':') {
        return {false, "", "invalid: expected colon after length"};
    }

    // Check for leading zeros (not allowed per netstring spec)
    if (colon_pos > 1 && input[0] == '0') {
        return {false, "", "invalid: leading zeros not allowed"};
    }

    // Parse the length
    std::size_t length = std::accumulate(
        input.begin(),
        input.begin() + static_cast<std::ptrdiff_t>(colon_pos),
        std::size_t{0},
        [](std::size_t acc, char c) {
            return acc * 10 + static_cast<std::size_t>(c - '0');
        });

    if (length > MAX_NETSTRING_PAYLOAD) {
        return {false, "", "invalid: payload exceeds maximum size"};
    }

    // Check if we have the complete payload + trailing comma
    std::size_t total_length = colon_pos + 1 + length + 1;
    if (input.size() < total_length) {
        return {false, "", "incomplete: waiting for payload"};
    }

    // Verify trailing comma
    if (input[colon_pos + 1 + length] != ',') {
        return {false, "", "invalid: missing trailing comma"};
    }

    // Extract payload
    std::string payload = input.substr(colon_pos + 1, length);
    bytes_consumed = total_length;

    return {true, payload, ""};
}

std::string serialize_netstring(const std::string& payload) {
    return std::to_string(payload.size()) + ':' + payload + ',';
}

}  // namespace platyplaty
