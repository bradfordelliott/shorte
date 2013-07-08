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

@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual


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
I wasn't happy with other markups like reStructuredText since I didn't
find it all that extensible and wanted something similar
to HTML that allowed attributes on tags without having
to go as far as XML.



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
- @include       | This tag is used to include another file (breaks conditional cascade)
- @include_child | This tag is used to include a child file (supports conditional cascade)

-& Other Tags
- @inkscape  | Include an SVG created in Inkscape
- @imagemap  | Include an HTML image map
- @sequence  | Generate a sequence diagram


@h1 The Document Header

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
The @image tag is used to include an image. Recommended image formats
currently included .jpg or .png.

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
Shorte was built with technical documentation in mind so it supports
including a variety of source code snippets. These are described in the
following section.

@h3 @c
This tag is used to embed C code directly into the document and
highlight it appropriately.

@shorte
\@c
#define XYZ "xyz"
printf("Hello world!\n");

@c
#define XYZ "xyz"
printf("Hello world!\n");

@h3 @python
This tag is used to embed Python code directly into the document and
highlight it appropriately.

@h3 @d
This tag is used to embed D code directly into the document and
highlight it appropriately.

@h3 @bash
This tag is used to embed bash code directly into the document and
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

@h3 @perl
This tag is used to embed Perl code directly into the document and
highlight it appropriately.

@h3 @shorte
This tag is used to embed Shorte code directly into the document and
highlight it appropriately.

@h3 @code
If the language is not supported by Shorte the @code tag can be
used to at least mark it as a block of code even if it can't properly
support syntax highlighting.


@h2 Include Files
Shorte supports include files using either of the following tags:

@table
- Include        | Description
- @include       | A normal include - interrupts any conditional text flow
- @include_child | A child include - obeys conditional text flow cascading rules

@h3 @include
The @include tag is used to include another file. This is to allow breaking
a document up into multiple modules. The @include will break any cascading of
conditional statements in the document hierarchy. To cascade conditional
text in the document hierarcy use the @include_child tag instead.

@shorte
\@include "chapters/my_chapter.tpl" 

@text
Includes also support conditionals in order to
support generating multiple documents from the same source. The example
below uses a command line conditional called *VARIABLE* to include
or exclude the file.

@shorte
\@include: if="VARIABLE == 'xyz'"
chapters/my_chapter.tpl
chapters/my_chapter2.tpl

@h3 @include_child
The @include_child tag is an alternative to the @child tag. It behaves
slightly differently in that it does not break the cascase of conditional
text but continues the current cascade.

@shorte
\@h1 My Title
This section will continue inside the my_chapter.tpl file.

\@include_child: if="VARIABLE == 'xyz'"
chapters/my_chapter.tpl

@h2 Other Tags
The following section describes some of the other more obscure
tags that Shorte supports.

@h3 @inkscape
This allows including SVG files from Inkscape direction in the document. It
requires Inkscape to be installed and the path properly configured. SVG files
are automatically converted to .png files for inclusion since SVG files aren't
widely supported.

@h3 @imagemap
This tag is used to generate an Image map. It currently only works in the
HTML output template.

@h3 @sequence
This tag is used to generate a sequence diagram.

