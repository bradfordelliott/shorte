@body

@h2 Text Entry Tags

@h3 @text
The @text tag creates a text block that is automatically
parsed for things like bullets, indentation, or blocks
of code.

@h Lists
You can insert lists:
@shorte: exec=True
\@text
- One
  - Two
    - Three
- Four
  - Five

@text
Creating numbered lists can be done by starting the list with
numbers as shown below. Currently the numbers are ignored but this will
be fixed in future versions.

@shorte: exec=True
\@text
1. One
    1. Two
        1. Three
2. Blah

@h Code Blocks
Text blocks can also contain code segments by indenting the
block by four spaces.

@shorte: exec=True
\@text
This is a random paragraph here

    This is an indented code block. You need a blank line
    before and after.
    
    indented code blocks can have paragraphs but the blank
    line above needs to have four spaces at the start or this
    block will be in a second code block. The code block
    should end with a blank line with no spaces.

    For example, these two blocks are split because the line
    above was completely blank and did not start with four spaces.
    
Here is the start of the next paragraph in the text block.


@h Syntax Highlighting Code
You can also syntax highlight code by using three backticks as shown
in the example below:

@shorte: exec=True
\@text
```c
int main(void)
{
    printf("Hello world!\\n");
}
```

@h Inline Styling
Another paragraph with @\{hl, some inlined styling\} and

- A second list

{{
and a block of code
}}

@text
When rendered we get something that looks like this:

@text
blah blah blah

- An multi-level list
  - A second level in the list
    - A third level in the list

Another paragraph with @{hl, some inlined styling} and

- A second list

{{
and a block of code
}}



@h3 @p
The @p tag is used to create a paragraph. It is similar to the *P* tag
in HTML. It does not attempt to parse the text block like the @text
tag does in order to extract lists or indented code.

@shorte: exec=True
\@p This is a paragraph in my document
\@p This is another paragraph in my document


@h3 @pre
The @pre tag creates a block of unformatted text:

@shorte: exec=True
\@pre
This is a test
  this is a test
    this is also a test


@h3 @markdown
The @markdown tag is similar to the @text tag with the following
exceptions:
- macros are not expanded
- markdown style headings are supported whereas they are not
  in the @text block.

@shorte: exec=True
\@markdown
##### A level 5 header
This is some random markdown text with some `inline code`


@include "chapters/inline_styling.tpl"
