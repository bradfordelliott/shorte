
@h3 @c
The @c tag is used to embed C code directly into the document and
highlight it appropriately. For example, the following block of code
inlines a C snippet. The code can also be run locally using g++ by
passing the exec="1" attribute. See Executing Snippets for
more information on setting up Shorte to execute code snippets.

@shorte:
\@c: exec="1"
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("hello world!\\n");
    return EXIT_SUCCESS;
}

@text
Executing the code block by adding the @{b,exec="1"} attribute
generates the following:
@c: exec="1"
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("hello world!\\n");
    return EXIT_SUCCESS;
}


