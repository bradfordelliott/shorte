
# Template #1
@template: name="one"
\#include <stdio.h>
\#include <stdlib.h>

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

@body
