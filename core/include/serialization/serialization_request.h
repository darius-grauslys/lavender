#ifndef SERIALIZATION_REQUEST_H
#define SERIALIZATION_REQUEST_H

#include "defines_weak.h"
#include <defines.h>

void initialize_serialization_request(
        Serialization_Request *p_serialization_request);

///
/// Either p_file_handler is non-null,
/// or the value of size_of__tcp_payload is meant to be set.
///
/// WARNING: be sure to >>DEACTIVATE<< before calling this a
/// second time on the same request. You will leak memory otherwise!
///
/// Returns false if fails to allocate tcp packet bitmap, pM_packet_bitmap
///
bool activate_serialization_request(
        Serialization_Request *p_serialization_request,
        void *p_file_handler,
        Quantity__u16 size_of__tcp_payload,
        bool is_serialization_request__tcp_or__io);

void deactivate_serialization_request(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Serialization_Request *p_serialization_request);

static inline
void set_serialization_request_as__allocated(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags |=
        SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED;
}

static inline
void set_serialization_request_as__deallocated(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags &=
        ~SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED;
}

static inline
void set_serialization_request_as__active(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags |=
        SERIALZIATION_REQUEST_FLAG__IS_ACTIVE;
}

static inline
void set_serialization_request_as__inactive(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags &=
        ~SERIALZIATION_REQUEST_FLAG__IS_ACTIVE;
}

static inline
void set_serialization_request_as__read(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags |=
        SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE;
}

static inline
void set_serialization_request_as__write(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags &=
        ~SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE;
}

static inline
void set_serialization_request_as__keep_alive(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags |=
        SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE;
}

static inline
void set_serialization_request_as__fire_and_forget(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags &=
        ~SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE;
}

static inline
void set_serialization_request_as__tcp(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags |=
        SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO;
}

static inline
void set_serialization_request_as__io(
        Serialization_Request *p_serialization_request) {
    p_serialization_request->serialization_request_flags &=
        ~SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO;
}

static inline
bool is_serialization_request__allocated(
        Serialization_Request *p_serialization_request) {
    return p_serialization_request->serialization_request_flags
        & SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED;
}

static inline
bool is_serialization_request__active(
        Serialization_Request *p_serialization_request) {
    return p_serialization_request->serialization_request_flags
        & SERIALZIATION_REQUEST_FLAG__IS_ACTIVE;
}

static inline
bool is_serialization_request__reading(
        Serialization_Request *p_serialization_request) {
    return p_serialization_request->serialization_request_flags
        & SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE;
}

static inline
bool is_serialization_request__writing(
        Serialization_Request *p_serialization_request) {
    return !is_serialization_request__reading(
            p_serialization_request);
}

static inline
bool is_serialization_request__keep_alive(
        Serialization_Request *p_serialization_request) {
    return p_serialization_request->serialization_request_flags
        & SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE;
}

static inline
bool is_serialization_request__fire_and_forget(
        Serialization_Request *p_serialization_request) {
    return !is_serialization_request__keep_alive(
            p_serialization_request);
}

static inline
bool is_serialization_request__tcp_or_io(
        Serialization_Request *p_serialization_request) {
    return p_serialization_request->serialization_request_flags
        & SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO;
}

#endif
