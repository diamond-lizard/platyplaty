// Netstring parsing and serialization for IPC protocol.
// Format: <length>:<payload>,
// See: https://cr.yp.to/proto/netstrings.txt

#ifndef PLATYPLATY_NETSTRING_HPP
#define PLATYPLATY_NETSTRING_HPP

#include <cstddef>
#include <string>

namespace platyplaty {

// Maximum payload size: 64KB
constexpr std::size_t MAX_NETSTRING_PAYLOAD = 65536;

// Maximum digits in length prefix (5 digits = 99999, but we cap at 65536)
constexpr std::size_t MAX_LENGTH_DIGITS = 5;

struct NetstringParseResult {
    bool success;
    std::string payload;
    std::string error;
};

// Parse a netstring from input buffer.
// On success, bytes_consumed indicates how many bytes were used.
// On failure, bytes_consumed is 0 and error contains the reason.
NetstringParseResult parse_netstring(
    const std::string& input,
    std::size_t& bytes_consumed);

// Serialize a payload into netstring format.
std::string serialize_netstring(const std::string& payload);

}  // namespace platyplaty

#endif  // PLATYPLATY_NETSTRING_HPP
