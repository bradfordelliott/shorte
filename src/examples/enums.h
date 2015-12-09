
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

/**
 * A public enum
 *
 * @requires
 *   This enum requires nothing special
 */
enum my_enum
{
    /** This is a test */
    e_test = 0
};


/**
 * A device select.
 *
 * Channel A
 * - ABC
 * - DEF
 *
 * Channel B
 * - XYZ
 * - ZYX
 *
 * @{note, This is some random note that may or may not
 *         be handled correctly by the API}
 */
typedef enum
{
    /** My first enum */
    e_one = 1,
    /** My second enum */
    e_two = 2,
    /** My third enum */
    e_three = 3,
}e_my_random_enum;



