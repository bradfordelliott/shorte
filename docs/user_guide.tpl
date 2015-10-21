# The beginning of the document is assumed to be the document
# header. As a convention normally the top level file will
# contain metadata about the document.

# The title of the document
@doctitle The Shorte Language

# The subtitle of the document
@docsubtitle Reference Manual

# A version number (can be overwritten from the command line)
@docversion 1.0.74

# A number to assign to the document
@docnumber 34567

@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual
- 1.0.58   | 15 Oct, 2013  | Updated the documentation to describe preliminary
                             install instructions, the new @h and @xml tags and
                             the procedure to assign wikiwords to headings.
- 1.0.67   | 23 Oct, 2014  | Cleanup of the shorte documentation in preparation
                             for publishing.
- 1.0.74   | 9 Oct, 2015   | Overhaul of the user guide to bring it up to date

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
Shorte documents generally end with a .tpl extension and follow the format:

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

@text
Like HTML they are split into a heading and a body. The heading is
everything before the @body tag.

@h2 Shorte Comments
Shorte currently supports single line comments using the \# character
at the beginning of a line:

@shorte
# This is a single line comment
# and a second line to the same single line comment
This is not a comment

@text
If you want to use the \# character elsewhere in the document it should normally
be escaped with a \\\\ character. This is not necessary inside source code blocks
such as @c, @java, @python or in markdown segments that start with @markdown.

Multi-line comments use a format similar to HTML:

@shorte
\<!-- This is a multi-line comment -->

@include chapters/conditional_text.tpl
@include chapters/includes.tpl

@h2 Shorte Tags
Shorte uses the @ character as a simple markup
character. Wherever possible it attempts to avoid
having an end character to make the document more
readable and simplify typing.

The following table describes the tags currently
supported by Shorte:

@table: title="Shorte Supported Tags"
- Tag | Description
-& Document Metadata (only in document header)
- TagDocTitle     | The title associated with the document
- TagDocSubtitle  | The subtitle associated with the document
- TagDocVersion   | The version associatied with the document
- TagDocNumber    | The number associated with the document
- TagDocRevisions | The revision history associated with the document

-* Document Body
-& Heading Tags
- @h1      | A top level header similar to H1 in HTML
- @h2      | A header similar to H2 in HTML
- @h3      | A header similar to H3 in HTML
- @h4      | A header similar to H4 in HTML
- @h5      | A header similar to H5 in HTML

-& Text Entry Tags
- @text      | A document text block
- @p         | A paragraph similar to the *P* tag from HTML
- @pre       | A block of unformatted test similar to the *PRE* tag from HTML
- @markdonw  | A block of markdown text

-& Includes
- @include       | This tag is used to include another file (breaks conditional cascade)
- @include_child | This tag is used to include a child file (supports conditional cascade)

-& Images and Image Maps 
- @image     | An inline image
- @imagemap  | Include an HTML image map

-& Lists
- @ul        | An un-ordered list
- @ol        | An ordered list

-s Tables
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

@include "chapters/example_document.tpl"

@include "chapters/document_header.tpl"

@h1 The Document Body

@include "chapters/tag_type_headings.tpl"

@include "chapters/tags/text.tpl"

@include "chapters/images.tpl"

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

@h2 Register Definitions
@include "chapters/tags/register.tpl"

@h2 Source Code Types
@include "chapters/tags/define.tpl"
@include "chapters/tags/enum.tpl"
@include "chapters/tags/struct.tpl"
@include "chapters/tags/functions.tpl"


@h2 Syntax Highlighting Code Segments
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


@h2 Acronyms
@include "chapters/tags/acronyms.tpl"



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

@h3 @embed
TBD - Add description of this tag


#@include "chapters/sequence_diagrams.tpl"

#@include "chapters/test_cases.tpl"

@include "chapters/command_line.tpl"

@include chapters/vim.tpl

@include "chapters/documenting_source_code.tpl"
