# The beginning of the document is assumed to be the document
# header. As a convention normally the top level file will
# contain metadata about the document.

# The title of the document
@doc.title The Shorte Language

# The subtitle of the document
@doc.subtitle Reference Manual

# A version number (can be overwritten from the command line)
@doc.version 1.0.74

# A number to assign to the document
@doc.number 34567

@doc.revisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual
- 1.0.58   | 15 Oct, 2013  | Updated the documentation to describe preliminary
                             install instructions, the new @h and @xml tags and
                             the procedure to assign wikiwords to headings.
- 1.0.67   | 23 Oct, 2014  | Cleanup of the shorte documentation in preparation
                             for publishing.
- 1.0.74   | 26 Oct, 2015  | A partial cleanup of the user guide. More work to
                             follow in version 1.0.75.

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
\@doc.title My Title
\@doc.subtitle My Subtitle
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
\<!-- This is a multi-line
      comment that wraps across
      multiple lines -->

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
- @markdown  | A block of markdown text

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
#- @vector    | Similar to @struct but generates a bitfield
- @struct    | A C style structure
- @prototype | C function prototypes
- @functionsummary | A function summary
- @typesummary     | A type summary

-& Source Code Tags
- @c      | A block of C code
#- @d      | A block of D code
- @bash   | A block of bash code
- @python | A block of python code
#- @sql    | A block of SQL code
- @java   | A block of Java code
- @tcl    | A block of TCL code
#- @vera   | A block of Vera code
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

# DEBUG BRAD: These need to be updated to really be useful
#@include "chapters/installation_instructions.tpl"

@include "chapters/example_document.tpl"

@include "chapters/document_header.tpl"

@h1 The Document Body

@include "chapters/tags/headings.tpl"

@include "chapters/tags/text.tpl"

@include "chapters/tags/image.tpl"

@include "chapters/tags/lists.tpl"
@include "chapters/tags/tables.tpl"


@h2 Notes, Warnings, TBD and Questions

@include "chapters/tags/note.tpl"
@include "chapters/tags/tbd.tpl"
@include "chapters/tags/warning.tpl"
@include "chapters/tags/question.tpl"



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

@h3 [[ExecutingSnippets,Executing Snippets]]
In many cases the code within these tags can be executed and the results captured
within the document itself. This is useful for validating example code.
Execution is done bu adding the following attribute:

    exec="1"

to the tag. Remote execution is also possible if SSH keys are setup by
adding the machine="xxx" and port="xxx" parameters.

@include "chapters/tags/c.tpl"
@include "chapters/tags/python.tpl"


@h3 @bash
This tag is used to embed bash code directly into the document and
highlight it appropriately.

@include "chapters/tags/perl.tpl"

@include "chapters/tags/shorte.tpl"
@include "chapters/tags/d.tpl"
@include "chapters/tags/sql.tpl"
@include "chapters/tags/java.tpl"
@include "chapters/tags/tcl.tpl"

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



@h2: if=0
Other Tags
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

@include "chapters/mergefiles.tpl"
@include "chapters/documenting_source_code.tpl"
