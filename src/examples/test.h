
/** the class keeps a doubly linked list of all instances of the class that have been created
 * insertion at the tail.  This list is used by the classes instance iterator
 * class_iterator_func refer to cs_mx_class_instances_iterator
 */
typedef struct cs_mx_handle_table_entry_tag
{
    /** This is a field */
    int one;
} head, tail;

struct cs_mx_handle_table_entry_tag * head, * tail;


typedef struct tag_name struct_alias;
struct tag_name struct_instance_1;
struct_alias struct_instance_2;

/**
 * This is a description of my function
 *
 * With another line here and some *bold* text.
 *
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
 * @param blah  [I] -
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
int func1(int blah2, bool* dummy);

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
 */
typedef struct {
    cs_t100_handle_t dev_id;     /**< Device Handle value */
    cs_t100_handle_t irq_handle; /**< IRQ Handle Value */
/* start bugzilla 28081 */
    cs_uint32        ireg_address; /**< Interrupt Register Address */
/* bugzilla end 28081 */
    cs_uint16        ireg_data;  /**< Current values of the interrupt register */
    cs_uint16        ereg_data;  /**< Current values of the enable register */
    cs_uint16        sreg_data;  /**< Current values of the status register,
                                  *   Will be 0 when there is no status
                                  *   register for a node */
    cs_uint8         slice;      /**< For interrupts with multiple instances,
                                  *   which instance has interrupted. */
    cs_uint8 xxx;
} cs_t100_irq_handler_data_t;


/**
 * This method is called to show the overall status of the device
 * for a particular set of slices. This method will not work properly
 * on simplex devices right now. This will be added in the future.
 *
 * This method is only defined if CS_DONT_USE_STDLIB is not defined
 * implying that the C standard library is available. It uses sprintf()
 * and the CS_PRINTF() macro to display output which may not be
 * possible on systems that do not have a console.
 *
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
 * @param slice_start         [I] - The slice to start the dump from
 * @param slice_end           [I] - The slice to end the dump at.
 * @param sections_to_display [I] - A mask defining the sections of the report
 *                                  to display.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 * 
 * @example
 *
 *     // Print the full status for slices 0-7
 *     cs4224_diags_show_status(0, 7, CS4224_STATUS_ALL);
 *
 *     // Only print the global information for slices 0-3
 *     cs4224_diags_show_status(0, 3, CS4224_STATUS_GLOBAL);
 */
cs_status cs4224_diags_show_status(
    cs_uint32 slice_start2,
    cs_uint32 slice_end,
    cs_uint16 sections_to_display);


/** This one should show up */
#define my_test2 0 /* TODO ccw consider making this dynamic */

/**
 * This one shouldn't show up
 *
 * @private
 */
#define my_test3 9


#define my_test4 0 /* This one shouldn't show up either because it has no header */




