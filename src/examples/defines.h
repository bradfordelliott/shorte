/** @file: defines.h
 *
 * @brief
 *
 * @h1 Defines
 */

/**
 * This is some random description of a define here
 *
 * @example
 *   int random_int = PUBLIC_DEFINE_ZERO
 *
 * @requires
 *   This method is only defined if PC_FLAG == 1
 */
#define PUBLIC_DEFINE_ZERO 0

/**
 * This define is public. It has a string
 * value.
 *
 * @requires
 *   This is only defined if PC_FLAG == 1
 */
#define PUBLIC_DEFINE_STRING "This is a public define"

/* This should not be shown */
#define PRIVATE_DEFINE_NO_COMMENT "This is a test"

/**
 * This define has a couple of characters
 * like & and < that should be escaped if
 * things work correctly.
 */
#define DEFINE_WITH_SPECIAL_CHARS ((1 << 23) & 0xFF)

/**
 * A private define
 *
 * @private
 */
#define PRIVATE_DEFINE_MARKED_PRIVATE 1

/**
 * This define has been deprecated
 *
 * @deprecated
 *   Don't use this define anymore. You should find
 *   something else
 */
#define DEPRECATED_DEFINE 1


#if 1

/** This is a public define */
#define PUBLIC_DEFINE_IN_IFDEF 1

#endif

#ifdef BRAD
#  if defined(XYZ)
#    define PUBLIC_DEFINE_NESTED_IFDEF 1
#  endif
#endif

