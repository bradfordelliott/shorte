
# Template #1
@template: name="one"
\#include <stdio.h>
\#include <stdlib.h>

int my_function(int val1 [], int val2 [][5])
{
    return 1;
}

int main(int argc, char* argv[])
{
$1
    return EXIT_SUCCESS;
}


# Template #2
@template: name="2"
import sys

handle = open("hello.bat", "rt")
contents = handle.read()
$1


# Template #3
@template: name="3"
gcc -o hello hello.c
./hello
$1

# Template #4
@template: name="structs"
\#include <stdio.h>
\#include <stdlib.h>

typedef struct
{
    const char* serial_number;
    const char* part_number;
}blah2;

int main(int argc, char* argv[])
{
$1
    return EXIT_SUCCESS;
}


# Template #5
@template: name="enums"
\#include <stdio.h>
\#include <stdlib.h>

typedef enum
{
    LOOPBK_HOST = 1,
    LOOPBK_LINE = 3,
}e_loopback_intf;

int main(int argc, char* argv[])
{
$1
    return EXIT_SUCCESS;
}

@body
