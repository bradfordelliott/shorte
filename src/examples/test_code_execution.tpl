@doc.title Code Execution
@doc.subtitle Examples
@doc.info
This file contains some example code snippets used to test
the automatic execution of code segments to validate their
behavior.

@body

@h1 Passing Examples
This file demonstrates the excution of source code blocks by
the shorte engine. In this section all the examples should pass
and the output should be displayed.

@h2 C
Test execution of @c blocks. The configuration parameters used
to execute the example are stored in the shorte.cfg file as:
@pre
c.compile.linux=
c.compile.osx=
c.compile.win32=

@c: exec=True run_args="--hello" compile_args="-DTEST"
#include <stdlib.h>
#include <stdio.h>

/**
 * The main routine
 *
 * @return
 *   Always returns EXIT_SUCCESS.
 */
int main(int argc, char* argv[])
{
    int i = 0;
#if defined(TEST)
    printf("Hello   world!\n\n");
#endif
    printf("This is a C example with a really long line in it "
           "that should wrap in the code output. I'm not sure what "
           "it will do to the output box\n\n");
    for(i = 0; i < argc; i++)
    {
        printf("argv[%d] = %s\n", i, argv[i]);
    }
    return EXIT_SUCCESS;
}

@h2 C++

@cpp: exec=True
#include <iostream>
#include <cstdlib>
using namespace std;

// The main routine
int main(void)
{
    /* Hello world! */
    cout << "Hello world\n";
    return EXIT_SUCCESS;
}

@h2 Python
Test execution of @python blocks.

@python: exec=True
import sys
print "Hello world!"


@h2 Bash
Test execution of @bash blocks

@bash: exec=True
echo "Hello"
pwd

@h2 Java
# Use the save parameter to get around the class name restriction
# of java where the public class has to match the file name.
@java: name=HelloWorldApp.java exec=True
class HelloWorldApp {
    public static void main(String[] args) {
        System.out.println("Hello world.");
        System.out.println("I am java!");
    }
}

@h2 Perl

@perl: exec=True
printf("Hello perl!\n");

@h2 TCL

@tcl: exec=True
puts "Hello TCL\n";

@h2 Swift
@swift: exec=True
let x=10;
let label = "This is a test"
let width = 94
print("Hello world\n");

@h2 Go
@go: exec=True
package main
import "fmt"
func main() {
    fmt.Println("Hello world!");
}

@h2 Javascript
@javascript: exec=True
var parts = ["hello", " ", "world", "!"]
var index;
var text = "";

for(index = 0; index < parts.length; index++)
{
    text += parts[index];
}

print(text)

@h2 Batch
@batch: exec=True
rem This is a test
echo Hello world!

@h2 XML
@xml
<!-- This is a comment -->
<one>
</one>


@h2 Shorte
@shorte: exec=True
\@text
This is a shorte textblock. I should be able to execute
to see the results.

@h1 Failing Examples

@h2 C
This section demonstrates the execution of C code in order
to trap errors in excuted code.

@h3 Test Compile Error
Trap compilation failure.
@c: exec=True ignore_errors=True
int main(void)
{
    printf(xxx);
}

@h3 Test Runtime Error
Trap runtime failures by checking the return code of non-zero.
@c: exec=True ignore_errors=True
#include <stdio.h>
#include <stdlib.h>
/* The main routine */
int main(void)
{
    printf("Hello world!\n");
    return EXIT_FAILURE; 
}

@h3 Test Return Code
Make sure the example returns the correct return code.
@c: exec=True ignore_errors=True
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("Hello world!\n");
    return -1;
}

@h2 Python

@h3 Test Compilation Failure
@python: exec=True ignore_errors=True
print "Hello world!"
sys.exit(0)

@h3 Test Runtime Failure
@python: exec=True ignore_errors=True
import sys
print "Hello world!"
sys.exit(-1)


@h2 Bash
Test failure detection in @bash blocks

@h3 Syntax Errors
@bash: exec=True ignore_errors=True
echo "Hello world!"
exit(-1)

@h3 Runtime Errors
@bash: exec=True ignore_errors=True
echo "Hello"
exit -1

@h2 Java
Testing Java execution

@h3 Syntax Errors
@java: name=HelloWorldApp.java exec=True ignore_errors=True
public static void main(String[] args) {
    System.out.println("Hello world.");
    System.out.println("I am java!");
}

@h4 Class name doesn't match file name
@java: exec=True ignore_errors=True
class HelloWorldApp {
    public static void main(String[] args) {
        System.out.println("Hello world.");
        System.out.println("I am java!");
        System.exit(-1);
    }
}


@h3 Runtime Errors
The following block of code demonstrates the detection
of a runtime error in a block of java code.

@java: name=HelloWorldApp.java exec=True ignore_errors=True
class HelloWorldApp {
    public static void main(String[] args) {
        System.out.println("Hello world.");
        System.out.println("I am java!");
        System.exit(-1);
    }
}

@text
This example demonstrates a thrown exception

@java: name=HelloWorldApp.java exec=True ignore_errors=True
class HelloWorldApp {
    public static void main(String[] args) throws Exception
    {
        System.out.println("Hello world.");
        System.out.println("I am java!");
        throw new Exception();
    }
}
