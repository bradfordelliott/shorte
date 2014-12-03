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
 * This is my example class
 */
class my_class
{
public:
    /** Constructor for the class object */
    my_class(void);

    int func1(void);

    /** This is func2 */
    int func2(void);

private:
    /** This is my private function */
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
