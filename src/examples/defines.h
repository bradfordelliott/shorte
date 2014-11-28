
/**
 * This is some random description of a define here
 *
 * @example
 *   int random_int = PUBLIC_DEFINE_ZERO
 */
#define PUBLIC_DEFINE_ZERO 0

/**
 * This define is public
 */
#define PUBLIC_DEFINE_STRING "This is a public define"

/* This should not be shown */
#define PRIVATE_DEFINE_NO_COMMENT "This is a test"

/**
 * A private define
 *
 * @private
 */
#define PRIVATE_DEFINE_MARKED_PRIVATE 1


#if 1

/** This is a public define */
#define PUBLIC_DEFINE_IN_IFDEF 1

#endif

#ifdef BRAD
#  if defined(XYZ)
#    define PUBLIC_DEFINE_NESTED_IFDEF 1
#  endif
#endif

