/** @file test.c
 *
 * @brief
 * This is some random data about this file here
 *
 * - One
 *     - Two
 *     - Three
 * -
 *
 * @{note, It should support an inline note}
 *
 */
#define FALSE 0
#define TRUE !FALSE

/**
 * @h1 Test.c
 * @h2 Function Summary: test.c
 * @functionsummary
 * @text
 * @table: name="This is my table!"
 * - Blah  | Blah 
 * - Three | Four
 */

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
 * @param blah  [I] -
 *     Some data associated with blah
 *     with some more data
 *
 *     @{table,
 *     - One   ! Two
 *     - Three ! Four
 *     }
 *
 *     This is more @{b,data}.
 *
 * @param dummy [O] - Some other dumb variable.
 *
 * @return TRUE on success, FALSE on failure.
 *
 * @example
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
 *             refer to my_test21 for future use.
 */
int test_dot_c_my_test(int blah, int* dummy)
{

    return TRUE;
}


/**
 * This is another test function
 *     @param blah [I] - This si a test
 *
 * @heading Blah Blah
 */
int test_dot_c_my_test21(int blah)
{
    return FALSE;
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

