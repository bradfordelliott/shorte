/** @file test.c
 *
 * @brief
 *
 * @h1 Test.c
 * This is some random data about this file here
 *
 * - One
 *     - Two
 *     - Three
 *
 * @{note, It should support an inline note}
 *
 */
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include "test.h"

int test_dot_c_my_test(int blah, int* dummy);

/**
 * This is some text related to the @h1 from the file brief
 * here.
 *
 * @h2 A function summary example
 * The following table is a function summary of this module.
 *
 * @functionsummary
 * @text
 * @table: name="This is my table!"
 * - Blah  | Blah 
 * - Three | Four
 *
 * @h1 [[WikiHeader, A Wiki Header]]
 * This is some random text here with a link to WikiHeader.
 *
 * @brief
 * This is an example of a define
 *
 * @example
 *   if(my_bool == FALSE):
 *   {
 *       printf("False value!\\n");
 *   }
 *
 * @since
 *   This version was introduced in version 1.2
 */
#define FALSE 0

/**
 * This is another define that is the opposite
 * of FALSE
 */
#define TRUE !FALSE


#if defined(BRAD)

#ifdef BLAH

#define test_dot_c_my_test2 0 /* TODO ccw consider making this dynamic */

#endif /* BLAH */

/**
 * This structure contains some statistics
 */
typedef struct {
    /**< Number of times aligner has entered LOF state during the last statistics interval. */
    cs_uint64 bei7erc1_stat;
    
    /**< Path Monitoring BEI error count for SECTION BEI */
    cs_uint64 bei7erc1_stat2;

} cs_term_stats_t, *cs_term_stats_p;


/**
 * A definition to parse with a description
 * that should act like a text block that
 * can support lists:
 *
 * - one
 *   - two
 * - three
 *
 * and inline tables:
 *
 * @{table,
 * -t One
 * - Three ! Four
 * }
 *
 * and more paragraphs
 */
#define TEST_DOT_C_TEST 0

#endif /* BRAD */

/** Another define
 * with a multi-line description
 * and a "quote" built-in */
#define TEST_DOT_C_BLAH_BLAH_BLAH "This is my define here"


/** 
 * This enum description has a list in it
 * - one
 *   - two
 *   - three
 * - four
 *
 * This is a new parapraph
 *
 * @{table,
 * -t One
 * -  Three ! Four
 * }
 *
 * and a new paragraph
 *
 * @{table,
 * -x Another table
 * -r A reserved row
 * -  This is a test
 * }
 *
 * @{tbd,
 * This still needs to be done}
 *
 * @heading My Heading
 *
 * @example
 *   e_test_dot_c_blah myenum;
 *   my_enum.xxx = 10;
 *   my_enum.yyy = 22;
 */
typedef enum
{
    /**
     * Some description of a
     * with a list
     * - One
     *   - Two
     *   - Three
     * - Four
     *
     * and a table:
     *
     * @{table,
     * -x One   ! two
     * -  Three ! Four
     * }
     */
    xxx = 1,

    /** Some value for b */
    yyy = 2,
}e_test_dot_c_blah;


/**
 * This is a description of mystruct
 * 
 * @{warning,
 * This is a warning inside the structure
 * description}
 *
 * @example
 *   mystruct_t tmp;
 *   tmp.a = 0;
 */
typedef struct
{
    /** This is a description of the field 'a' */
    int a;

    /** This is a description of field 'b' */
    char* b;
}test_dot_c_mystruct_t;

/** THis is a test
 *
 * @example: src="examples/mystruct2.c"
 */
typedef struct
{
    /** Test */
    int y;

}test_dot_c_mystruct2_t;

/**
 * The supported PRBS polynomials 
 *
 * With a list
 * - one
 *   - two
 * - three
 * - four
 *
 * And another paragraph
 *
 * And still another paragraph
 *
 * And a new list
 *
 * - a new list
 *   - a list item
 *
 * Some @{i, italic text} and some @{b, bold text}.
 *
 * @{note,
 *     This should be a note
 *     with a list inside of it but it probably doesn't
 *     work.
 *     
 *     - one
 *     - two
 *     - three
 * }
 */
typedef enum
{
    /** 1 + x^28 + x^31
     * - a list
     *   - a subitem
     * - Some *bold* data
     *
     * A new paragraph */
    CS4224_PRBS_Tx_2exp31 = 0x0,

    /**
     * 1 + x^18 + x^23
     * 
     * With a table
     *
     * @{table,
     * - One  ! Two  ! Three
     * - Four ! Five ! Six
     * }
     */
    CS4224_PRBS_Tx_2exp23 = 0x1,
    
    /**
     * 1 + x^14 + x^15
     *
     * @{note, Should not really use this. This should be a list but it doesn't appear to work.
     *
     *  - one
     *  - two
     *  }
     */
    CS4224_PRBS_Tx_2exp15 = 0x2,

    /** 1 + x^6 + x^7  */
    CS4224_PRBS_Tx_2exp7 = 0x3,
    
    /** 1 + x^4 + x^9  */
    CS4224_PRBS_Tx_2exp9 = 0x4,

    /** 1 + x^5 + x^9  */
    CS4224_PRBS_Tx_2exp9_5 = 0x5,

    /** 1 + x^5 + x^58  */
    CS4224_PRBS_Tx_2exp58 = 0x6,

}e_test_dot_c_cs4224_prbs_polynomial;




/**
 * This is another test function
 *
 * @note
 *   This is a random note here
 *
 * @param blah [I] - This is a test
 *
 * @preconditions
 *   What has to happen before the function is called
 *
 * @postconditions
 *   What happens after the function is called
 *
 * @sideeffects
 *   Are there any side-effects caused by calling the function?
 *
 * @statespace
 *   Is there any state used by the function?
 *
 * @return Always returns FALSE.
 *
 * @todo
 *   I need to update shorte to support handing
 *   the if attribute on example tags as shown
 *   in the example below.
 *
 * @example: if("DEFINE1")
 * Include this example only if DEFINE1 is set
 *
 * @example: if("DEFINE2")
 * Include this example only if DEFINE2 is set
 */
int test_dot_c_my_test21(int blah)
{
    return test_dot_c_my_test(blah, NULL);
}


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
 *
 * @return
 *   This method returns:
 *   - TRUE on success
 *   - FALSE on failure.
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
int test_dot_c_my_test(int blah, int* dummy)
{

    return TRUE;
}

/**
 * @h2 Another heading
 * This is a brief description of this heading
 *
 *
 * @brief
 * This method has is public but has no parameters and
 * no return value.
 */
void test_doc_function_no_return(void)
{
}

int test_dot_c_my_undocumented_function(int main)
{
}

/**
 * @private
 */
int test_dot_c_my_private_function(void)
{
}

/**
 * This method has a requirement associated
 * with it.
 *
 * @param arg1 [I] - This is a random argument value.
 *
 * @requires
 *   This method is only defined if PC_FLAG == 1
 */
bool test_func_with_requirements(bool arg1)
{
    return false;
}

int main(void)
{
    return 0;
}
