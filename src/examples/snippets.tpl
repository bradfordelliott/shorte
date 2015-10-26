@doctitle Snippet Handling
@docsubtitle Shorte Examples
@doc.info
This file is used to demonstrate the process of handling code
snippets that can be used to simplify code segments by allowing
substitutions

@body

# Include the snippet templates
@include "examples/snippet_templates.tpl"
@h1 Snippet Handling

@h2 Snippet Template 1 
This example demonstrates the use of templates and code execution. The
@{b,show_template} parameter is set to False to hide the template itself
and @{b,show_full_source} is set to True so that the full source of the
example is available under the @{b,View Source} menu.

@c: save="hello.c" template=one exec=True indent=4 show_template=False show_full_source=True
printf("hello world #1!\n");
printf("hello world #2!\n");
printf("executing this block of code in template \"1\"\n");

@h2 Snippet Template 2
@python: exec="True" template="2" ignore_errors=True show_template=False
handle.close()
print contents
sys.exit(-1)

@h1 More Snippets

@h2 Snippet Template 3
Now execute a bash script with the contents of the
original hello world program which we saved in hello.c
@bash: save="hello.sh" exec="True" template="3"
exit 0

@text
This is some more text

@h1 Test Error Handling
This is a heading

@h4 h4
This is another heading

@h4 h42
This is a final heading
