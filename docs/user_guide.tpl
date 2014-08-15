# The beginning of the document is assumed to be the document
# header. As a convention normally the top level file will
# contain metadata about the document.

# The title of the document
@doctitle The Shorte Language

# The subtitle of the document
@docsubtitle Reference Manual

# A version number (can be overwritten from the command line)
@docversion 1.0.58

# A number to assign to the document
@docnumber 34567

@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual
- 1.0.58   | 15 Oct, 2013  | Updated the documentation to describe preliminary
                             install instructions, the new @h and @xml tags and
                             the procedure to assign wikiwords to headings.


# Shorte documents are split into a header and a body
# similar to an HTML document. The body tag defines
# the start of the body of the document.
@body

@h1 About the Shorte Language
The Shorte language is a text based programming language
used to generate documentation in a format that is familar
to writing source code. It supports:
- include files for modularizing a document
- conditional includes and conditional text
- easy revision control and diffing of documentation
- cross referencing of C source code 

@h2 Why another Language?
I started this project about two years ago because I wasn't happy
with other markups like reStructuredText. There are a lot of really
good markup tools out there but I decided to try my hand and creating
my own since I could easily extend it and make it do what I wanted.

I wanted a markup language similar to HTML but not as verbose
where I could sections within a document and have optional modifiers
or attributes on tags to have more control over the document.

I also wanted the tool to be able to automatically cross reference
my source code and pull it in similar to Doxygen but I found doxygen
hard to format quite like I wanted.


@h2 Document Structure
Shorte documents generally end with a .tpl extension and follow the format

@shorte
# Document heading here
\@doctitle My Title
\@docsubtitle My Subtitle
...

# The beginning of the body
\@body
\@h1 Some title here
Some text here
...

@h2 Shorte Comments
Shorte currently only supports single line comments using the \# character
at the beginning of a line.

@shorte
# This is a single line comment
# and a second line to the same single line comment
This is not a comment

@text
If you want to use the \# character elsewhere in the document it should normally
be escaped with a \\ character. This is not necessary inside source code blocks
such as @c, @java, @python, etc.

@h2 Conditional Text
The Shorte language supports two types of conditional text
- PHY style inline blocks
- conditionals using the if="xxx" attribute on tags

@h3 PHY Style Code Blocks
These blocks of code are similar to the inline PHY syntax. You use
the \<\? ... \?\> syntax to inline a block of Python code. Any output
must get assigned to a variable called *result* which gets return in
its expanded form. In this way you can conditionally generate text
or use Python to create documentation.

Variables can be passed to the interpreter using the *-m* command
line parameter.

@shorte
\<\?
result = ''
if(1):
    result += 'This is some *bold text* here'
if(0):
    result += 'But this line is not included' 
\?\>

@text
When output you will see something like:

<?
result = ''
if(1):
    result += 'This is some *bold text* here'
if(0):
    result += 'But this line is not included' 
?>

@h3 Conditional Attributes
Conditional test is also supported using the *if=* attribute on a tag.
For example:

@shorte
# Include this table
\@table: if="1"
- Col 1 | Col2
- Data1 | Data 2

# But not this table
\@table: if="0"
- Col 3  | col 4
- Data 3 | Data 4

@text
will expand to:

# Include this table
@table: if="1"
- Col 1 | Col2
- Data1 | Data 2

# But not this table
@table: if="0"
- Col 3  | col 4
- Data 3 | Data 4

@text
As will the inline code blocks you can specify variables to pass
to the *if* text to evaluate using the *-m* command line paramter.


@h2 Include Files
Shorte supports include files. There are two tags, @include and @include_child
which are used to include files.

They can be included anywhere in the body of the document.

@shorte
\@body
\@include "chapters/chapter_one.tpl"
\@include "chapters/chapter_two.tpl"

\@include: if="ALLOW_CHAPTER3 == True"
chapters/chapter_three.tpl

# Here we'll use the @include_child tag since
# the @include tag normally breaks the flow of
# conditional statements. By using @include_child
# this file will only be included if ALLOW_CHAPTER3 == True
\@include_child "chapters/child_of_chapter_three.tpl"

@note
Shorte currently can't handle include paths. The include path has to
be a sub-directory where the top level file is included. Eventually
support for include paths will be added.

@h2 Inline Formatting
TBD: Add description of this section


@h2 Shorte Tags
Shorte uses the @ character as a simple markup
character. Wherever possible it attempts to avoid
having an end character to make the document more
readable and simplify typing. The document is entered
by the use of tags that have the syntax @tag.

The following table describes the tags currently
supported by Shorte:

@table: title="Shorte Supported Tags"
- Tag | Description
-& Document Metadata (only in document header)
- @doctitle     | The title associated with the document
- @docsubtitle  | The subtitle associated with the document
- @docversion   | The version associatied with the document
- @docnumber    | The number associated with the document
- @docrevisions | The revision history associated with the document

-* Document Body
-& Heading Tags
- @h1 | A top level header similar to H1 in HTML
- @h2 | A header similar to H2 in HTML
- @h3 | A header similar to H3 in HTML
- @h4 | A header similar to H4 in HTML
- @h5 | A header similar to H5 in HTML

-& Text Entry Tags
- @text      | A document text block
- @p         | A paragraph similar to the *P* tag from HTML
- @pre       | A block of unformatted test similar to the *PRE* tag from HTML

-& Includes
- @include       | This tag is used to include another file (breaks conditional cascade)
- @include_child | This tag is used to include a child file (supports conditional cascade)

-& Images and Image Maps 
- @image     | An inline image
- @imagemap  | Include an HTML image map

-& Lists and Tables
- @ul        | An un-ordered list
- @ol        | An ordered list
- @table     | A table

-& Notes, TBDs and Questions
- @note      | A note
- @question  | A question
- @tbd       | A To Be Determined block
- @questions | A list of questions

-& Structures and Functions
- @define    | A C style \#define
- @enum      | An enumeration
- @vector    | Similar to @struct but generates a bitfield
- @struct    | A C style structure
- @prototype | C function prototypes
- @functionsummary | A function summary
- @typesummary     | A type summary

-& Source Code Tags
- @c      | A block of C code
- @d      | A block of D code
- @bash   | A block of bash code
- @python | A block of python code
- @sql    | A block of SQL code
- @java   | A block of Java code
- @tcl    | A block of TCL code
- @vera   | A block of Vera code
- @perl   | A block of Perl code
- @code   | A block of unknown source code
- @shorte | A block of shorte code
- @xml    | A block of XML code


-& Other Tags
- @shell           | TBD
- @inkscape        | Include an SVG created in Inkscape
- @checklist       | Generate a checklist
- @acronyms        | A list of acronyms
- @embed           | An embedded object (HTML only)

-& Sequence Diagrams
- @sequence        | Generate a sequence diagram

-& Test Case Definitions
- @testcase        | A test case description
- @testcasesummary | A test case summary

@include "chapters/installation_instructions.tpl"

@include "chapters/command_line.tpl"


@h1 The Document Header
The first part of any Shorte document is the document header. It is
structured like HTML but isn't a strict. It is basically anything
in the document before the @body tag. An example document header looks like:

@shorte
# The beginning of the document is assumed to be the document
# header. As a convention normally the top level file will
# contain metadata about the document.

# The title of the document
\@doctitle The Shorte Language

# The subtitle of the document
\@docsubtitle Reference Manual

# A version number (can be overwritten from the command line)
\@docversion 1.0

# A number to assign to the document
\@docnumber 34567

\@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual


@h3 @doctitle
The @doctitle defines the title associated with the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@h3 @docsubtitle
The @docsubtitle defines a subtitle for the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@h3 @docversion
The @docversion tag defines a version number for the document. This can be overridden
at the command line.

@h3 @docnumber
The @docnumber tag defines a number to associate with the document.

@h3 @docrevisions
The @docrevisions tag defines a revision history for the document.


@h1 The Document Body

@h2 Heading Tags
Headings use the @hN format where *N* currently
ranges from 1-5.

@h3 @h1
The @h1 tag is the highest level header. It is similar in use
to the H1 tag from HTML.

@shorte
# An example header
\@h1 This is an example header
This is some text for the example header

@h3 @h2
The @h2 tag is a hierarchial header directly beneath
the @h1 tag. It is similar to the H2 tag from HTML.

@shorte
\@h1 This is an example header

# An example second level header
\@h2 This is a sub header
This is some text related to the sub @h1 tag.

@h3 @h3
The @h3 tag is a hierarchial header directly beneath
the @h2 tag. It is similar to the H3 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header
Some text related to this header

@h3 @h4
The @h4 tag is a hierarchial header directly beneath
the @h3 tag. It is similar to the H4 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header

\@h4 This is a fourth level header
Some example text here

@h3 @h5
The @h5 tag is a hierarchial header directly beneath
the @h4 tag. It is similar to the H5 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header

\@h4 This is a fourth level header

\@h5 This is a fifth level header
Some example text here

@h3 @h
The @h tag can be used to create a header that is
un-numbered.

@shorte
\@h This is an un-numbered header
Some random text after the header

@h3 Assigning Wikiwords
Sometimes it is desirable to assign wikiwords to a heading. This
allows multi-word headings to be automatically linked but also allows
the user to prevent a short heading from being automatically linked

@shorte
\@h2: wikiword="MyHeading"
Test

This is some text associated with MyHeading. MyHeading will be expanded
to the word "Test" but Test won't get expanded.


@h2 Text Entry Tags

@h3 @text
The @text tag creates a text block that is automatically
parsed for things like bullets, indentation, or blocks
of code.

@shorte
blah blah blah

- An multi-level list
  - A second level in the list
    - A third level in the list

Another paragraph with \@\{hl, some inlined styling\} and

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

@shorte
\@p This is a paragraph in my document
\@p This is another paragraph in my document

@text
This creates a two paragraphs that looks like:

@p This is a paragraph in my document
@p This is another paragraph in my document

@h3 @pre
The @pre tag creates a block of unformatted text:

@shorte
\@pre
This is a test
  this is a test
    this is also a test

@text
When rendered it will look like:
@pre
This is a test
  this is a test
    this is also a test

@include "chapters/includes.tpl"

@include "chapters/images.tpl"

@h2 Lists and Tables
@include "chapters/lists.tpl"
@include "chapters/tables.tpl"

@h2 Notes, TBD and Questions

@h3 @note
The @note tag is used to create notes within a section. Here is an
example:

@shorte
\@note
This is a note here that I want to display

- It has a list
  - With some data

And another paragraph.

@text
This renders to something like this:

@note
This is a note here that I want to display

- It has a list
  - With some data

And another paragraph.


@h3 @tbd
The @tbd tag is used to highlight sections of a document
that are still *To Be Determined*. They are similar in
syntax to the @note tag

@shorte
\@tbd
This is a block of code that is to be determined. It
works just like a textblock and supports

- lists
    - indented data
    - another item
- second item in list

Another paragraph

    some indented text here
    that wraps to a new line

A final paragraph

@tbd
This is a block of code that is to be determined. It
works just like a textblock and supports

- lists
    - indented data
    - another item
- second item in list

Another paragraph

    some indented text here
    that wraps to a new line

A final paragraph

@h3 @question
The @question tag is used to mark a question to the reader
or mark anything that might still need to be answered

@shorte
\@question
This is a question

with another paragraph. It should eventually be switched
to the same syntax as the @note and @tbd tag.

@text
When rendered this looks like:

@question
This is a question

with another paragraph. It should eventually be switched
to the same syntax as the @note and @tbd tag.

@h3 @questions
The @questions tag is used to create a Q and A type section.
For example,

@shorte
\@questions
Q: This is a question with some more info
A: This is the answer to the question with a lot
   of detail that wraps across multiple lines and
   hopefully it will make the HTML look interesting
   but I'm not sure we'll just have to see what
   happens when it's rendered

Q: This is another question with some more information
A: This is the answer to that question

@text
Will render to:

@questions
Q: This is a question with some more info
A: This is the answer to the question with a lot
   of detail that wraps across multiple lines and
   hopefully it will make the HTML look interesting
   but I'm not sure we'll just have to see what
   happens when it's rendered

Q: This is another question with some more information
A: This is the answer to that question

@h2 Structures and Functions

@include "chapters/structs_and_vectors.tpl"

@h3 @define
The @define is used to document a \#define structure in C.

@h3 @enum
The @enum tag is used to define an enumeration.

@enum: name="e_my_test" caption="This is a test enum" description='This is a test enum'
--values:
- Name | Value | Description
- LEEDS_VLT_SUPPLY_1V_TX | 0x0 |  1V supply TX 
- LEEDS_VLT_SUPPLY_1V_RX | 0x1 |  1V supply RX 
- LEEDS_VLT_SUPPLY_1V_CRE | 0x2 |  1V supply digital core 
- LEEDS_VLT_SUPPLY_1V_DIG_RX | 0x3 |  1V supply digital RX 
- LEEDS_VLT_SUPPLY_1p8V_RX | 0x4 |  1.8V supply RX 
- LEEDS_VLT_SUPPLY_1p8V_TX | 0x5 |  1.8V supply TX 
- LEEDS_VLT_SUPPLY_2p5V | 0xf |  2.5V supply 
- LEEDS_VLT_SUPPLY_TP_P | 0x9 |  Test point P 
- LEEDS_VLT_SUPPLY_TP_N | 0x8 |  Test point N 


@include "chapters/functions.tpl"


@h2 Source Code Tags
Shorte was built with technical documentation in mind so it supports
including a variety of source code snippets. These are described in the
following section.

@h3 Executing Snippets
In many cases the code within these tags can be executed and the results captured
within the document itself. This is useful for validating example code.
Execution is done bu adding the following attribute:

    exec="1"

to the tag. Remote execution is also possible if SSH keys are setup by
adding the machine="xxx" and port="xxx" parameters.

@h3 @c
The @c tag is used to embed C code directly into the document and
highlight it appropriately. For example, the following block of code
inlines a C snippet. The code can also be run locally using g++ by
passing the exec="1" attribute. See [[->Executing Snippets]] for
more information on setting up Shorte to execute code snippets.

@shorte
\@c: exec="0"
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("hello world!\n");
    return EXIT_SUCCESS;
}

@text
This renders the following output:

@c: exec="0"
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("hello world!\n");
    return EXIT_SUCCESS;
}

@h3 @python
This tag is used to embed Python code directly into the document and
highlight it appropriately. If the code is a complete snippet it can
also be executed on the local machine and the results returned. See [[->Executing Snippets]]
for more information on setting up Shorte to execute code snippets.

@shorte
\@python: exec="1"
print "Hello world!"

@text
This will execute the code on the local machine and return the output:

@python:
print "Hello world!"

@h3 @bash
This tag is used to embed bash code directly into the document and
highlight it appropriately.

@h3 @perl
This tag is used to embed Perl code directly into the document and
highlight it appropriately.

@h3 @shorte
This tag is used to embed Shorte code directly into the document and
highlight it appropriately.

@h3 @d
This tag is used to embed D code directly into the document and
highlight it appropriately.

@h3 @sql
This tag is used to embed SQL code directly into the document and
highlight it appropriately.

@h3 @java
This tag is used to embed Java code directly into the document and
highlight it appropriately.

@h3 @tcl
This tag is used to embed TCL code directly into the document and
highlight it appropriately.

@h3 @vera
This tag is used to embed Vera code directly into the document and
highlight it appropriately.

@h3 @code
If the language is not supported by Shorte the @code tag can be
used to at least mark it as a block of code even if it can't properly
support syntax highlighting.

@shorte
\@code
This is a test of a language that isn't supported by
Shorte.

@code
This is a test of a language that isn't supported by
Shorte.

@h3 @shell
TBD: add description of this tag.

@h3 @xml
This tag can be used to insert a block of XML tag in
a document and highlight it appropriately. Note that you
currently have to escape the <\? sequence to prevent it from
being expanded by shorte.

@shorte
\@xml
<\?xml version="1.0"?>
<methodCall>
  <methodName>dev.dev_reg_read</methodName>
  <params>
    <param>
      <!-- The die being accessed (in decimal) -->
      <value><i4>1</i4></value>
    </param>
    <param>
      <!-- The address of the register being accessed (in decimal) -->
      <value><i4>0</i4></value>
    </param>
  </params>
</methodCall>

@xml
<\?xml version="1.0"?>
<methodCall>
  <methodName>dev.dev_reg_read</methodName>
  <params>
    <param>
      <!-- The die being accessed (in decimal) -->
      <value><i4>1</i4></value>
    </param>
    <param>
      <!-- The address of the register being accessed (in decimal) -->
      <value><i4>0</i4></value>
    </param>
  </params>
</methodCall>





@h2 Other Tags
The following section describes some of the other more obscure
tags that Shorte supports.

@h3 @inkscape
This allows including SVG files from Inkscape direction in the document. It
requires Inkscape to be installed and the path properly configured. SVG files
are automatically converted to .png files for inclusion since SVG files aren't
widely supported.




@h3 @checklist
The @checklist tag creates a non-interactive checklist
@checklist: title="test" caption="test"
- one: caption="blah blah blah" checked="yes"
- two
- three: checked="yes"
- four


@h3 @acronyms
@acronyms
- Acronym | Definition
- EPT     | Egress Parser Table
- EPC     | Egress Parser CAM



@h3 @embed
TBD - Add description of this tag


#@include "chapters/sequence_diagrams.tpl"

#@include "chapters/test_cases.tpl"

