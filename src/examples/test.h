/** @file test.h
 *
 * @brief
 *
 * @h1 Test.h: Section 1
 * This is a description of this test file
 */

/** @cond SHORTE
 * @h1 Test.h: Section 2!!!!
 * This is a test block with some random data here. For
 * some reason this breaks the parsing of func1
 *
 * @table
 * - One | Two
 * - Three | Four
 *
 * @text
 * Blah blah blah
 *
 * @h2 Test.h: Function Summary
 * @functionsummary
 * @text
 * @endcond
 */
/*
class myclass
{
public:
    myclass(void)
    {
    }
};
*/

/** the class keeps a doubly linked list of all instances of the class that have been created
 * insertion at the tail.
 *
 * @example
 *    tail.one = 0;
 * 
 */
typedef struct handle_table_entry_tag_s
{
    /** This is a field */
    int one;
} head, tail;

/**
 * This is a description of my private enum
 *
 * @private
 * @deprecated This enum shouldn't be used anymore
 */
typedef enum
{
    /** This is a test */
    e_private_test = 0
}test_dot_h_my_private_enum;

/**
 * @h1 This is a test
 * This is some random info here
 *
 * @brief
 * This is a description of my public enum
 * 
 * A second paragraph
 *
 * @example: exec=True
 *   if(curr_val == e_public_test)
 *   {
 *       printf("Found e_public_test");
 *   }
 *
 * @since
 *   version 1.0.2
 */
typedef enum public_enum_s
{
    /** This is a test */
    e_public_test = 0,

    /** This is a second field */
    e_public_test2 = 10
}public_enum;

struct handle_table_entry_tag * phead, * ptail;



//typedef struct tag_name struct_alias;
//struct tag_name struct_instance_1;
//struct_alias struct_instance_2;

/**
 * @cond SHORTE
 * @h2 Section 2!!!!
 * This is a test block with some random data here. For
 * some reason this breaks the parsing of func1
 *
 * @table
 * - One | Two
 * - Three | Four
 *
 * @text
 * Blah blah blah
 *
 * @endcond
 */

/**
 * This is a description of my function
 *
 * With another line here and some *bold* text.
 *
 * @cond SHORTE
 * @{table,
 * -t Title of my table here
 * -h One   ! Two
 * -  Three ! Four
 * }
 *
 * This is a list with some checkboxes
 * -[ ] one
 * -[x] two
 *     - blah
 *     -[x] blah2
 * -[ ] three
 * -[x] four
 *
 *
 * @param blah2  [I] -
 *     Some dumb variable that behaves like
 *     a text block with a list
 *
 *     -[x] one
 *         - two
 *     -three
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
 *     - One   ! Two
 *     - Three ! Four
 *     }
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
 *
 * @endcond
 *
 * @return TRUE on success, FALSE on failure.
 */
int func1(int blah2, void* dummy);

/**
 * This is a private function that won't normally be extracted.
 * It can be forcibly extracted by setting:
 *
 *    cpp_parser.extract_private=1
 *
 * @param blah  [I] - A parameter
 * @param dummy [I] - Another parameter
 *
 * @private
 */
int private_func1(int blah, char* dummy);


/**
 * This is the structure that gets passed to an application registered
 * interrupt handler.
 *
 * @example
 *    irq_handler_data_t handler;
 *    handler.dev_id     = NULL;
 *    handler.irq_handle = NULL;
 */
typedef struct {
    /** Hello ! */
    int  dev_id;       /**< Device Handle value */
    int  irq_handle;   /**< IRQ Handle Value */
    int  ireg_address; /**< Interrupt Register Address */
    int  ireg_data;    /**< Current values of the interrupt register */
    int  ereg_data;    /**< Current values of the enable register */
    int  sreg_data;    /**< Current values of the status register,
                         * Will be 0 when there is no status
                         * register for a node */
    int  slice;        /**< For interrupts with multiple instances,
                         * which instance has interrupted. */
    int  xxx;
} irq_handler_data_t;


/**
 * This method is called to show the overall status of the device
 * for a particular set of slices. This method will not work properly
 * on simplex devices right now. This will be added in the future.
 *
 * This method is only defined if CS_DONT_USE_STDLIB is not defined
 * implying that the C standard library is available. It uses sprintf()
 * and the CS_PRINTF() macro to display output which may not be
 * possible on systems that do not have a console.
 
 * Here is an image
 * 
 * @{image,src="examples/gallery/two.jpg}
 *
 * And an animated image
 *
 * @{img,src="examples/gallery/1.gif}
 *
 * @cond SHORTE
 * @{table,
 * -t SERDES Status
 * -h Column  ! Description
 * - Sl       ! The slice number
 * - Lock     ! Whether or not the lock detector is locked
 * - LockI    ! The current value of the lock detect interrupt register
 * - Freq     ! The VCO frequency slot
 * - EDC MD   ! The configured EDC mode such as CX1, SR, etc.
 * - CTRLA    ! The main cursor
 * - CTRLB    ! The pre and post cursors
 * - Squelch  ! 1 if the TX is squelched, 0 if not
 * - Temp     ! The measured temperature from the die
 * - 1.8V     ! The measured voltage of the die
 * - 0.9V     ! The measured voltage of the die
 * }
 *
 *
 * @return CS_OK on success, CS_ERROR on failure.
 * 
 * @example
 *
 *     // Print the full status for slices 0-7
 *     my_diags_show_status(0, 7, DIAGS_STATUS_ALL);
 *
 *     // Only print the global information for slices 0-3
 *     my_diags_show_status(0, 3, DIAGS_STATUS_GLOBAL);
 *
 * @pseudocode
 *     This is some randome info
 *     and some more code here
 *     with a while loop:
 *
 *     while(1)
 *     {
 *     }
 *
 *     and some other stuff
 * @endcond
 */
int my_diags_show_status(
    /** [I] - The starting slice */
    int slice_start2,
    /** [I] - The ending slice */
    int slice_end,
    /** [I] - A mask defining the sections of the report to display */
    int sections_to_display);


/** This one should show up */
#define my_test2 0 /* TODO ccw consider making this dynamic */



/**
 * This one shouldn't show up
 *
 * @private
 */
#define my_test3 9


#define my_test4 0 /* This one shouldn't show up either because it has no header */


/**
 * This structure has been deprecated. Don't
 * use it anymore
 *
 * @deprecated
 *   I deprecated this because it doesn't do
 *   anything
 *
 * @since
 *   This was introduced in version 1.0
 *   @{note, This is an inline note}
 */
typedef struct
{
    /** The first parameter */
    int tmp1;
}deprecated_struct;


/**
 * This enum is deprecated
 * 
 * @deprecated
 * This enum is not useful.
 * @{note, An embedded note}
 *
 * @example
 *   int x = (int)dep_one;
 *   int y = (int)dep_two;
 */
typedef enum
{
    dep_one = 1,
    dep_two = 2
}deprecated_enum;
