#include "platform.h"
#include <debug/debug.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void debug_info__verbose(const char *msg_fmt, ...) {
#ifndef NLOG
#ifdef VERBOSE
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[37;1m(V) info:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);
    
    printf("\n");
#endif
#endif
}

void debug_warning__verbose(const char *msg_fmt, ...) {
#ifndef NLOG
#ifdef VERBOSE
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[33;1m(V) warning:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);
    
    printf("\n");
#endif
#endif
}

void debug_info(const char *msg_fmt, ...) {
#ifndef NLOG
#ifndef NDEBUG
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[30;1minfo:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);
    
    printf("\n");
#endif
#endif
}

void debug_warning(const char *msg_fmt, ...) {
#ifndef NDEBUG
#ifndef NLOG
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[33;1mwarning:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);
    
    printf("\n");
#endif
#endif
}

void debug_error(const char *msg_fmt, ...) {
#ifndef NDEBUG
#ifndef NLOG
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[31;1merror:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);

    printf("\n");

    // create core dump, but keep going.
    PLATFORM_coredump();
#endif
#endif
}

void debug_abort(const char *msg_fmt, ...) {
    PLATFORM_pre_abort();
#ifndef NDEBUG
#ifndef NLOG
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[31;1mabort:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);

    printf("\n");

#endif
#endif
    PLATFORM_abort();
}
