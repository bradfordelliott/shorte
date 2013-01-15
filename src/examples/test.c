
/** A definition to parse */
#define TEST 0

/** Another define
 * with a multi-line description
 * and a "quote" built-in */
#define BLAH_BLAH_BLAH "This is my define here"


/** My Enum */
typedef enum
{
    /** Some description of a */
    a = 1,

    /** Some value for b */
    b = 2,
}blah;


/**
 * This is a description of my function
 *
 * With another line here and some *bold* text.
 *
 * @param blah  [I] - Some dumb variable
 * @param dummy [O] - Some other dumb variable.
 *
 * @return TRUE on success, FALSE on failure.
 *
 * @example
 *     int blah = 0;
 *     bool dummy = TRUE;
 *
 *     // The @text doesn't work properly and comments
 *     // aren't showing up in the parsed text
 *     dummy = @blah;
 *
 *     my_test(blah,dummy);
 *
 * @see
 *     my_test21
 */
int my_test(int blah, bool* dummy)
{

    return TRUE;
}


/** This is another test function
 * @param blah [I] - This si a test
 */
int my_test21(int blah)
{
    return FALSE;
}
