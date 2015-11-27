#include <stdio.h>
#include <stdlib.h>


/** This is a test function
 *
 * @return Just junk for now
 */
int test(void)
{
    return 0;
}


/**
 * This is my example class with an inline
 * list:
 *
 * - one
 *     - two
 * - three
 */
class my_class
{
public:
    /** Constructor for the class object */
    my_class(void);

    int func1(void);

    /**
     * This is func2
     * 
     * @param arg1 [I] - This is the first argument
     *                   and it contains a nested list
     *                   - a
     *                       - b
     *                   - c
     *
     * @return
     *     It returns some random data
     *     with a list
     *     - one
     *     - two
     */
    int func2(int arg1);

private:
    /**
     * This is my private function
     *
     * @private
     *     Shorte can't always extract private methods properly
     *     so need to manually mark it private for now.
     */
    void priv_func1(void);

    /** Private member */
    int tmp;

};

/**
 * The main application method
 *
 * @return Always 0
 */
int main(void)
{
    my_class m;

    return 0;
}
