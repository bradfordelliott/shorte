
/**
 * This is a description of my function
 *
 * With another line here and some *bold* text.
 *
 * @{table,
 * -t Title of my table here
 * -h One   | Two
 * -  Three | Four
 * }
 *
 * @param blah  [I] -
 *     Some dumb variable that behaves like
 *     a text block with a list
 *
 *     - one
 *         - two
 *     - three
 *
 *     And a new paragraph and a table
 *
 *     @{table,
 *     - One
 *     - Two
 *     } 
 *
 * @param dummy [O] -
 *     Some other dumb variable.
 *
 *     With a new paragraph and some @{b,bold} text
 *     and a list:
 *
 *     - list
 *       - list1
 *       - list2
 *
 *     and a table
 *     @{table,
 *     - One | Two
 *     - Three | Four
 *     }
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
int func1(int blah, bool* dummy);

