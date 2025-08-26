#ifndef IPV4_ADDRESS_H
#define IPV4_ADDRESS_H

#include "defines.h"

bool populate_ipv4_address(
        IPv4_Address *p_ipv4_address,
        const char *p_ip_address__cstr,
        const char *p_port__cstr);

#endif
