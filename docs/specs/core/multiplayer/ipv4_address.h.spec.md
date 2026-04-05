# Specification: core/include/multiplayer/ipv4_address.h

## Overview

Provides parsing and population of `IPv4_Address` structs from string
representations. This is the lowest-level addressing primitive in the
multiplayer system, used by `TCP_Socket` and `TCP_Socket_Manager` to
identify remote endpoints.

## Dependencies

- `defines.h` (for `IPv4_Address`, `u8`, `u16`)

## Types

### IPv4_Address (struct)

    typedef struct IPv4_Address_t {
        u8 ip_bytes[4];
        u16 port;
    } IPv4_Address;

| Field | Type | Description |
|-------|------|-------------|
| `ip_bytes` | `u8[4]` | Four octets of the IPv4 address in network order. |
| `port` | `u16` | Port number for the connection endpoint. |

## Functions

### Parsing

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `populate_ipv4_address` | `(IPv4_Address *p_ipv4_address, const char *p_ip_address__cstr, const char *p_port__cstr) -> bool` | `bool` | Parses the IP address and port from C-strings and populates the provided `IPv4_Address`. Returns true on success, false on parse failure. |

## Agentic Workflow

### Usage Pattern

`IPv4_Address` is a value type used to describe connection endpoints.
It is populated once from user-provided strings and then passed by
value or pointer to socket operations:

    IPv4_Address addr;
    populate_ipv4_address(&addr, "192.168.1.1", "7777");
    // addr is now ready for use with TCP_Socket operations.

### Preconditions

- `p_ipv4_address` must be non-null.
- `p_ip_address__cstr` must be a valid null-terminated dotted-decimal
  IPv4 string (e.g. `"192.168.1.1"`).
- `p_port__cstr` must be a valid null-terminated numeric string
  representing a port number within `u16` range.

### Postconditions

- On success: `ip_bytes` contains the four parsed octets and `port`
  contains the parsed port number.
- On failure: the contents of `p_ipv4_address` are unspecified.

### Error Handling

- Returns `false` if either string cannot be parsed into a valid
  IPv4 address or port number.
