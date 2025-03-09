#ifndef TEST_UTIL__LOG_H
#define TEST_UTIL__LOG_H

#include <stdio.h>

static inline
void test_util__log(const char *msg_fmt, ...) {
    va_list args_list;
    va_start(args_list, msg_fmt);
    printf("\033[33;1mTEST LOG:\033[0m ");
    vprintf(msg_fmt, args_list);
    va_end(args_list);
    
    printf("\n");
}

#endif
