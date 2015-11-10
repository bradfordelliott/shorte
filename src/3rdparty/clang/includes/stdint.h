#ifndef _STDINT_H
#define _STDINT_H
#include <stddef.h>

/* 7.18.1.5  Greatest-width integer types */
typedef long long  intmax_t;
typedef unsigned long long   uintmax_t;

#ifndef NULL
#    define NULL ((void*)0)
#endif

#define offsetof(type, field) ((size_t)&((type *)0)->field)

#endif
