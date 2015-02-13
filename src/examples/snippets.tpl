@doctitle Snippet Handling
@docsubtitle Shorte Examples

@template: name="1"
\#include <stdio.h>
\#include <stdlib.h>

int main(int argc, char* argv[])
{
    $1
    return EXIT_SUCCESS;
}


@body
@h1 Snippet Handling

@python: exec="True"
handle = open("hello.bat", "rt")
contents = handle.read()
handle.close()
print contents

@c: save="hello.c" template="1" exec="True"
printf("hello world!\\n");
printf("executing this block of code in template \"1\"\\n");

@bash: exec="True"
gcc -o hello hello.c
./hello
