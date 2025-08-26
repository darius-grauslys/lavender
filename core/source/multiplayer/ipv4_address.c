#include "multiplayer/ipv4_address.h"
#include "defines_weak.h"
#include "lav_string.h"

bool populate_ipv4_address(
        IPv4_Address *p_ipv4_address,
        const char *p_ip_address__cstr,
        const char *p_port__cstr) {
    IPv4_Address ipv4_address;
    memset(&ipv4_address, 0, sizeof(ipv4_address));
    u32 index_of__ip_address__cstr = 0;
    for (Index__u8 index_of__ip_byte = 0;
            index_of__ip_byte < 4;
            index_of__ip_byte++) {
        u8 ip_byte;
        for (i8 length_of__byte_chars = 3;
                length_of__byte_chars > 0;
                length_of__byte_chars--) {
            if (cstr_to_u8__limit_n(
                        &p_ip_address__cstr[index_of__ip_address__cstr], 
                        length_of__byte_chars, 
                        &ip_byte)) {
                index_of__ip_address__cstr += length_of__byte_chars + 1;
                break;
            }
            if (length_of__byte_chars == 1)
                return false;
        }
        ipv4_address.ip_bytes[index_of__ip_byte] = ip_byte;
    }

    u16 port;
    if (!cstr_to_u16__limit_n(
                p_port__cstr, 
                6, 
                &port)) {
        return false;
    }

    ipv4_address.port = port;
    *p_ipv4_address = ipv4_address;

    return true;
}
