# The beginning of the document is assumed to be the document
# header. As a convention normally the top level file will
# contain metadata about the document.

# The title of the document
@doctitle The Shorte Language

# The subtitle of the document
@docsubtitle Reference Manual

# A version number (can be overwritten from the command line)
@docversion 1.0

# A number to assign to the document
@docnumber 34567

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
- @image     | An inline image
- @ul        | An un-ordered list
- @ol        | An ordered list
- @table     | A table
- @note      | A note
- @question  | A question
- @tbd       | A To Be Determined block
- @struct    | A structure
- @define    | A \#define
- @vector    |
- @shell     |
- @prototype |

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

-& Includes
- @include       | 
- @include_child |

-& Other Tags
- @inkscape  |
- @imagemap  |
- @sequence  | Generate a sequence diagram


@h1 The Document Header

@h3 @doctitle
The @doctitle defines the title associated with the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@h3 @docsubtitle
The @docsubtitle defines a subtitle for the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@h3 @docversion
TBD

@h3 @docnumber
TBD

@h3 @docrevisions
TBD


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

Another paragraph with @{hl, With some inlined styling} and

- A second list

{{
and a block of code
}}


@h3 @p
The @p tag is used to create a paragraph. It is similar to the *P* tag
in HTML.

@h3 @pre
The @pre tag creates a block of unformatted text

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

@h3 @image
@h3 @ul
@h3 @ol
@h3 @table
@h3 @note
@h3 @tbd
@h3 @question
@h3 @tbd
@h3 @struct
@h3 @define
@h3 @vector
@h3 @shell
@h3 @prototype


@h2 Source Code Tags

@h3 @c
@h3 @d
@h3 @bash
@h3 @python
@h3 @sql
@h3 @java
@h3 @tcl
@h3 @vera
@h3 @perl
@h3 @code
@h3 @shorte

@h2 Includes
Shorte supports include files using either of the following tags:

@table
- Include        | Description
- @include       | A normal include - interrupts any conditional text flow
- @include_child | A child include - obeys conditional text flow cascading rules

@h3 @include
@h3 @include_child

@h2 Other Tags

@h3 @inkscape
@h3 @imagemap
@h3 @sequence

