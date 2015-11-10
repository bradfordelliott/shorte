#ifndef _STDINT_H
#define _STDINT_H
#include <stddef.h>

/* 7.18.1.1  Exact-width integer types */
typedef signed char int8_t;
typedef unsigned char   uint8_t;
typedef short  int16_t;
typedef unsigned short  uint16_t;
typedef int  int32_t;
typedef unsigned   uint32_t;
typedef long long  int64_t;
typedef unsigned long long   uint64_t;

/* 7.18.1.5  Greatest-width integer types */
typedef long long  intmax_t;
typedef unsigned long long   uintmax_t;

#ifndef NULL
#    define NULL ((void*)0)
#endif

#define offsetof(type, field) ((size_t)&((type *)0)->field)

#endif
