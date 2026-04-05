#include <multiplayer/test_suite_multiplayer_ipv4_address.h>

#include <multiplayer/ipv4_address.c>

TEST_FUNCTION(populate_ipv4_address__valid_input__returns_true) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "192.168.1.1", "7777");
    munit_assert_true(result);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__valid_input__parses_first_octet) {
    IPv4_Address addr;
    populate_ipv4_address(&addr, "192.168.1.1", "7777");
    munit_assert_uint8(addr.ip_bytes[0], ==, 192);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__valid_input__parses_second_octet) {
    IPv4_Address addr;
    populate_ipv4_address(&addr, "192.168.1.1", "7777");
    munit_assert_uint8(addr.ip_bytes[1], ==, 168);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__valid_input__parses_third_octet) {
    IPv4_Address addr;
    populate_ipv4_address(&addr, "192.168.1.1", "7777");
    munit_assert_uint8(addr.ip_bytes[2], ==, 1);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__valid_input__parses_fourth_octet) {
    IPv4_Address addr;
    populate_ipv4_address(&addr, "192.168.1.1", "7777");
    munit_assert_uint8(addr.ip_bytes[3], ==, 1);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__valid_input__parses_port) {
    IPv4_Address addr;
    populate_ipv4_address(&addr, "192.168.1.1", "7777");
    munit_assert_uint16(addr.port, ==, 7777);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__zeroes__parses_correctly) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "0.0.0.0", "0");
    munit_assert_true(result);
    munit_assert_uint8(addr.ip_bytes[0], ==, 0);
    munit_assert_uint8(addr.ip_bytes[1], ==, 0);
    munit_assert_uint8(addr.ip_bytes[2], ==, 0);
    munit_assert_uint8(addr.ip_bytes[3], ==, 0);
    munit_assert_uint16(addr.port, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__max_octets__parses_correctly) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "255.255.255.255", "65535");
    munit_assert_true(result);
    munit_assert_uint8(addr.ip_bytes[0], ==, 255);
    munit_assert_uint8(addr.ip_bytes[1], ==, 255);
    munit_assert_uint8(addr.ip_bytes[2], ==, 255);
    munit_assert_uint8(addr.ip_bytes[3], ==, 255);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__localhost__parses_correctly) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "127.0.0.1", "8080");
    munit_assert_true(result);
    munit_assert_uint8(addr.ip_bytes[0], ==, 127);
    munit_assert_uint8(addr.ip_bytes[1], ==, 0);
    munit_assert_uint8(addr.ip_bytes[2], ==, 0);
    munit_assert_uint8(addr.ip_bytes[3], ==, 1);
    munit_assert_uint16(addr.port, ==, 8080);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__null_ip_string__returns_false) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, (const char *)0, "7777");
    munit_assert_false(result);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__null_port_string__returns_false) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "192.168.1.1", (const char *)0);
    munit_assert_false(result);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__empty_ip_string__returns_false) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "", "7777");
    munit_assert_false(result);
    return MUNIT_OK;
}

TEST_FUNCTION(populate_ipv4_address__empty_port_string__returns_false) {
    IPv4_Address addr;
    bool result = populate_ipv4_address(&addr, "192.168.1.1", "");
    munit_assert_false(result);
    return MUNIT_OK;
}

DEFINE_SUITE(ipv4_address,
    INCLUDE_TEST__STATELESS(populate_ipv4_address__valid_input__returns_true),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__valid_input__parses_first_octet),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__valid_input__parses_second_octet),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__valid_input__parses_third_octet),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__valid_input__parses_fourth_octet),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__valid_input__parses_port),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__zeroes__parses_correctly),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__max_octets__parses_correctly),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__localhost__parses_correctly),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__null_ip_string__returns_false),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__null_port_string__returns_false),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__empty_ip_string__returns_false),
    INCLUDE_TEST__STATELESS(populate_ipv4_address__empty_port_string__returns_false),
    END_TESTS)
