
/**
 * This is a description of my function
 *
 * With another line here and some *bold* text.
 *
 * And a table
 * @{table,
 * - One  ! Two  ! Three
 * - Four ! Five ! Six
 * }
 *
 * @{question,
 * What should I do here?}
 *
 * @{note,
 * This is a random note here that contains a list
 * - one
 *     - two
 * -}
 *
 * @param blah  [I] -
 *     Some data associated with blah
 *     with some more data
 *
 *     @{table,
 *     - One   ! Two
 *     - Three ! Four
 *     }
 *
 *     and a note
 *
 *     @{note,
 *     - This is a note that is really a list
 *     }
 *
 *     This is more @{b,data}.
 *
 * @param dummy [O] - Some other dumb variable.
 * @param dummy2 [out] - Another description.
 * @param dummy3 [in]  - Another input parameter.
 * @param dummy4 [in]  - Another input parameter.
 * @param dummy5 [in]  - Some random description.
 * @param dummy6 [I/O] - An in/out parameter.
 * @param dummy7 [I]   - Some other stuff.
 * @param dummy8 [I]   - Some other stuff.
 *
 * @return TRUE on success, FALSE on failure.
 *
 * @example
 *     0         1         2         3         4         5         6         7
 *     01234567890123456789012345678901234567890123456789012345678901234567890123456789
 *     int blah = 0;
 *     int dummy = TRUE;
 *
 *     // The text doesn't work properly and comments
 *     // aren't showing up in the parsed text
 *     dummy = blah;
 *
 *     if(1)
 *     {
 *         my_test(blah,dummy);
 *     }
 *
 * @see
 *     test_dot_c_my_test21
 *
 * @deprecated This method has been deprecated. Please
 *             refer to my_test21 for future use. Can deprecated
 *             contain a note:
 *             @{note,
 *             This is a random note here}
 */
int test_dot_c_my_test(
    int blah,
    int* dummy,
    int dummy2,
    int dummy3,
    int dummy4,
    int dummy5,
    unsigned long long dummy6,
    unsigned long long dummy7,
    unsigned long long dummy8)
{

    return TRUE;
}
