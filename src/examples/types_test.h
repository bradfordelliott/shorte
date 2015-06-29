
/* The clang parser should be able to find mytypes.h in the platform
 * directory in order to parse the standard types */
#include "mytypes.h"

/**
 * @h2 Checking stdint.h
 *
 * @brief
 *
 * This is a test function that uses stdint types
 *
 * @param one   [I] - A test parameter
 * @param two   [I] - A second test parameter
 * @param three [O] - A third test parameter.
 *
 * @return Always zero for now.
 */
uint32_t test1(uint32_t one, uint16_t two, uint16_t* three[])
{
    return 0;
}
