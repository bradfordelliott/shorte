@doctitle Batch Files
@docsubtitle Batch File Tests

@template: name="1"
This is another template


@body
@h1 Batch Files
This is an example of a batch file

@batch: save="hello.bat" exec="True"
rem This is a comment
call "hello.bat"
echo Hello world

@python: exec="True"
handle = open("hello.bat", "rt")
contents = handle.read()
handle.close()
print contents

@c: save="hello.c"
#include <stdio.h>

int main(void)
{
    printf("hello world!\n");
    return 0;
}

@bash: exec="True"
gcc -o hello hello.c
./hello
