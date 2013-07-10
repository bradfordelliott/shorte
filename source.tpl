@h1 About the Shorte Language

@text
The Shorte language is a text based programming language
used to generate documentation in a format that is familar
to writing source code. It supports:
- include files for modularizing a document
- conditional includes and conditional text
- easy revision control and diffing of documentation
- cross referencing of C source code 

@h2 Why another Language?

@text
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

@text
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

@text
Shorte currently only supports single line comments using the # character
at the beginning of a line.

@shorte
# This is a single line comment
# and a second line to the same single line comment
This is not a comment

@text
If you want to use the # character elsewhere in the document it should normally
be escaped with a \ character. This is not necessary inside source code blocks
such as @c, @java, @python, etc.

@h2 Conditional Text

@text
The Shorte language supports two types of conditional text
- PHY style inline blocks
- conditionals using the if="xxx" attribute on tags

@h3 PHY Style Code Blocks

@text
These blocks of code are similar to the inline PHY syntax. You use
the <? ... ?> syntax to inline a block of Python code. Any output
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

This is some *bold text* here

@h3 Conditional Attributes

@text
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

@table: if="1"
- Col 1 | Col2
- Data1 | Data 2

@text
As will the inline code blocks you can specify variables to pass
to the *if* text to evaluate using the *-m* command line paramter.

@h2 Include Files

@text
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

@text
TBD: Add description of this section

@h2 Shorte Tags

@text
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
- @define    | A C style #define
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

@h1 The Command Line

@text


@bash
$ shorte.py -h
Usage: shorte.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILES, --files=FILES
                        The list of files to generate
  -l FILE_LIST, --list=FILE_LIST
                        The list of files to generate in an input file
  -o OUTPUT_DIR, --output=OUTPUT_DIR
                        The directory where output is generated
  -v VERSION, --version=VERSION
                        The version of the document
  -t THEME, --theme=THEME
                        The output theme
  -n NAME, --name=NAME  The document name or title
  -p PACKAGE, --package=PACKAGE
                        The output package. Supported types are html, odt,
                        word, and pdf
  -b OUTPUT_FORMAT, --output_format=OUTPUT_FORMAT
                        Set the output format in C generated code: bitfields,
                        byte_array, or defines
  -y, --diagnostic_code
                        Generate diagnostic code in generate code
  -c CONFIG, --config=CONFIG
                        The config file to load
  -s SETTINGS, --settings=SETTINGS
                        A list of settings to use that overrides the standard
                        config file
  -x PARSER, --parser=PARSER
                        The parser to use
  -a, --about           About this program
  -m MACROS, --macros=MACROS
                        Macro substitution
  -d DEFINE, --define=DEFINE
                        Macro substitution
  -r REPLACE, --search_and_replace=REPLACE
                        An input search and replace module that is loaded to
                        pre-process input files and replace any references

@h2 Some Command Line Examples

@text

Parse a list of source files defined by source_file_list.py and generate
Shorte modules describing each of the source files.

@bash
shorte.py -l source_file_list.py -x cpp -p shorte -r bin/cs4224_snr.py -m 'SKU=CS4343;VERSION=1.1'; -o build-output/srcs

@text
- The *-r cs4224_snr.py* file allows a search and replace to be performed on the sources as they are
  generated.
- The *-m flag* passes a list of macros that can be used within the
  document for conditional inclusion or conditional text.
- The *-o build-output/srcs* parameter says to generate the files in the
  build-output/srcs directory.
- The *-x cpp* option switches the parser to the CPP parser instead of
  the default Shorte parser.
- The *-p shorte* parameter says to generate Shorte code from the C sources.

@text
The source_file_list.py file will look something like:

@python
result = '''
modules/high_level/cs4224.c
modules/high_level/cs4224.h

# Only include FC-AN and KR-AN in the duplex guide
if(SKU == 'CS4343'):
    result += '''
modules/kran/cs4224_kran.c
'''

@h1 The Document Header

@text
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

@text
The @doctitle defines the title associated with the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@h3 @docsubtitle

@text
The @docsubtitle defines a subtitle for the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@h3 @docversion

@text
The @docversion tag defines a version number for the document. This can be overridden
at the command line.

@h3 @docnumber

@text
The @docnumber tag defines a number to associate with the document.

@h3 @docrevisions

@text
The @docrevisions tag defines a revision history for the document.

@h1 The Document Body

@text


@h2 Heading Tags

@text
Headings use the @hN format where *N* currently
ranges from 1-5.

@h3 @h1

@text
The @h1 tag is the highest level header. It is similar in use
to the H1 tag from HTML.

@shorte
# An example header
\@h1 This is an example header
This is some text for the example header

@h3 @h2

@text
The @h2 tag is a hierarchial header directly beneath
the @h1 tag. It is similar to the H2 tag from HTML.

@shorte
\@h1 This is an example header

# An example second level header
\@h2 This is a sub header
This is some text related to the sub @h1 tag.

@h3 @h3

@text
The @h3 tag is a hierarchial header directly beneath
the @h2 tag. It is similar to the H3 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header
Some text related to this header

@h3 @h4

@text
The @h4 tag is a hierarchial header directly beneath
the @h3 tag. It is similar to the H4 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header

\@h4 This is a fourth level header
Some example text here

@h3 @h5

@text
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

@text


@h3 @text

@text
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

@text
The @p tag is used to create a paragraph. It is similar to the *P* tag
in HTML. It does not attempt to parse the text block like the @text
tag does in order to extract lists or indented code.

@shorte
\@p This is a paragraph in my document
\@p This is another paragraph in my document

@text
This creates a two paragraphs that looks like:

@p
This is a paragraph in my document

@p
This is another paragraph in my document

@h3 @pre

@text
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

@h2 Include Files

@text
Shorte supports include files using either of the following tags:

@table
- Include        | Description
- @include       | A normal include - interrupts any conditional text flow
- @include_child | A child include - obeys conditional text flow cascading rules

@h3 @include

@text
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

@text
The @include_child tag is an alternative to the @child tag. It behaves
slightly differently in that it does not break the cascase of conditional
text but continues the current cascade.

@shorte
\@h1 My Title
This section will continue inside the my_chapter.tpl file.

\@include_child: if="VARIABLE == 'xyz'"
chapters/my_chapter.tpl

@h2 Images and Image Maps

@text


@h3 @image

@text
The @image tag is used to include an image. Recommended image formats
currently included .jpg or .png.

@h3 @imagemap

@text
This tag is used to generate an Image map. It currently only works in the
HTML output template. Links are not currently supported.

@shorte
\@imagemap: id="one"
- shape  | coords         | Label       | Description
- circle | 50,50,50       | A Circle    | This is a description of my circle
- rect   | 72,144,215,216 | A rectangle | This is a description of my rectangle.

\@image: map="one" src="chapters/images/imagemap.png"

@text
Will generate the following imagemap:

@imagemap: id="one"
- shape  | coords         | Label       | Description
- circle | 50,50,50       | A Circle    | This is a description of my circle
- rect   | 72,144,215,216 | A rectangle | This is a description of my rectangle.

@image: map="one" src="chapters/images/imagemap.png"


@h2 Lists and Tables

@text


@h3 @ul

@text
The @ul tag is used to create an unordered list similar to the *ul* tag
in HTML. Lists can currently be indented 5 levels deep.

@shorte
\@ul
- Item 1
  - Subitem a
    - Sub-subitem y
- Item 2
  - Subitem b

@text
This generates the following output

@ul
- Item 1
  - Subitem a
    - Sub-subitem y
- Item 2
  - Subitem b

@h3 @ol

@text
The @ol tag is used to create an unordered list similar to the *ol* tag
in HTML. Lists can currently be indented 5 levels deep.

@shorte
\@ol
- Item 1
  - Subitem a
    - Sub-subitem y
- Item 2
  - Subitem b

@text
This generates the following output

@ol
- Item 1
  - Subitem a
    - Sub-subitem y
- Item 2
  - Subitem b

@h3 @table

@text
The @table tag is used to create a table. The syntax is shown in the
example below.

@shorte
\@table
- Header Col 1 | Header Col 2
- Field 1      | Field 2
- Field 3      | Field 4
-& Section
- Field 5      | Field 6

@text
This generates the following output:

@table
- Header Col 1 | Header Col 2
- Field 1      | Field 2
- Field 3      | Field 4
-& Section Header
- Field 5      | Field 6

@h4 Spanning Columns

@text


@text
Spanning columns is accomplished by using one or more ||
after the column to span. Each additional | spans an extra column.

@shorte
\@table
- Column 1 | column 2 | Column 3 | Column 4 | Column 5
- This column spans the whole table
-& So does this header
- || Blah blah || Blah blah
-& This row has no spanning
- one | two | three | four | five

@text
This creates a table that looks like this:

@table
- Column 1 | column 2 | Column 3 | Column 4 | Column 5
- This column spans the whole table
-& So does this header
- || Blah blah || Blah blah
-& This row has no spanning
- one | two | three | four | five

@h4 Headings and Sub-headings

@text


@text
The first row in the table is generally treated as the header. You can
mark any row as a header row by staring the line with -*

@shorte
- My Heading 1
-* Also a heading
-& This is a sub-heading

@text
This creates a table that looks like:

@table
- My Heading 1
-* Also a heading
-& This is a sub-heading

@h4 Table Caption

@text
To create a caption for a table you can do the following:

@shorte
\@table: caption="This is a caption for my table"
- My table
- My data | some more data

@text
This creates the following table:

@table: caption="This is a caption for my table"
- My table
- My data | some more data

@h4 Table Title

@text
To add a title to the table you can use the *title* attribute:

@shorte
\@table: title="This is my table"
- My table
- My data | some more data

@text
This creates the following table:

@table: title="This is my table"
- My table
- My data | some more data

@h2 Notes, TBD and Questions

@text


@h3 @note

@text
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

@text
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

@text
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

@text
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

@text


@h3 @struct

@text
The @struct tag defines a C style structure. It also supports generating
a picture showing the layout of the structure. The *title* attribute
should currently be a unique name since it is used to map any generated
image to the structure itself as well as generate C code from the structure
definition.

For example:

@shorte
\@struct: title="struct1" caption="blah blah" diagram="show:yes,align:128,bitorder:decrement"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
Will generate:

@struct: diagram="show:yes,align:128,bitorder:decrement" caption="This is a caption. It is currently in the wrong place" treat_fields_as="bytes" title="struct1"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
Another example:

@shorte
\@struct: title="struct2" caption="blah blah"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
Will generate a structure without a picture:

@struct: caption="This is a caption. It is currently in the wrong place" treat_fields_as="bytes" title="struct2"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
The bit order can also be reversed and the alignment can be changed:

@shorte
\@struct: title="struct3" caption="This is a caption. It is currently in the wrong place" diagram="show:yes,align:64,bitorder:increment"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@struct: diagram="show:yes,align:64,bitorder:increment" caption="This is a caption. It is currently in the wrong place" treat_fields_as="bytes" title="struct3"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@h3 @vector

@text
The @vector is similar to the @struct tag and creates a bitfield type containing multiple fields.
Field sizes are generally outlined in bit ranges instead of bytes in the @struct tag. 

The following structure defines a 128 bit long bitfield with the bits shown in little endian
order on a 64 bit boundary.

@shorte
\@vector: title="vector1" caption="blah blah" diagram="show:yes,align:64,bitorder:increment"
- Field  | Name       | Description
- 0-8    | Blah       | Blah blah
- 10     | *Reserved* | Reserved for future use
- 12     | My field   | da da da

- 32-63  | TBD        | Something here
- 64-127 | field2     | This is a description

@text
This renders to the following:

@struct: diagram="show:yes,align:64,bitorder:increment" caption="" title="vector1"
- Field  | Name       | Description
- 0-8    | Blah       | Blah blah
- 10     | *Reserved* | Reserved for future use
- 12     | My field   | da da da

- 32-63  | TBD        | Something here
- 64-127 | field2     | This is a description

@text
This is an example of the Ethernet Header shown in little endian format:

@shorte
\@vector: title="Ethernet Header" caption="" diagram="show:yes,align:32,bitorder:decrement"
- Field   | Name          | Description
- 0-47    | Dest Addr     | The destination MAC address
- 48-95   | Source Addr   | The source MAC address
- 96-111  | Ethernet Type | The ethernet type
- 112-159 | Data          | Variable length data field

@text
Which renders to:

@struct: diagram="show:yes,align:32,bitorder:decrement" caption="" title="Ethernet Header"
- Field   | Name          | Description
- 0-47    | Dest Addr     | The destination MAC address
- 48-95   | Source Addr   | The source MAC address
- 96-111  | Ethernet Type | The ethernet type
- 112-159 | Data          | Variable length data field

@h3 @define

@text
The @define is used to document a #define structure in C.

@h3 @enum

@text
The @enum tag is used to define an enumeration.

@enum: caption="This is a test enum" name="e_my_test"
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

@h3 @prototype

@text
The @prototype is used to describe a function prototype. This might be used
when architecting code or it can also be extracted from existing source code (Currently
only C sources can be parsed).

@shorte
\@prototype: language="c"
- function: my_function
- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. For kicks
    we'll link to the EPT acronym
- prototype:
    int my_function(int val1 [], int val2 [][5]);
- returns:
    TRUE on success, FALSE on failure
- params:
    -- val1 | I | 
            1 = blah blah
                and more blah blah
                plus blah

            2 = blah blah blah

            0 = turn beacon on
    -- val2 | I |
            *1* = blah blah

            *2* = blah blah blah
- example:
    rc = my_function(val);

    if(rc != 0)
    {
        printf("Uh oh, something bad happened!\n");
    }

- pseudocode:

    // Blah blah blah
    _call_sub_function()

    if(blah)
    {
        // Do something else
        _call_sub_function2()
    }
    
- see also:
    THis is a test

@text
When rendered it will create output similar to the following
with it's own header automatically added for wiki linking. This behavior
may be controlled by the *prototype_add_header* field in the Shorte config file.

@h4: language="c"
my_function

@prototype: language="c"
- function: my_function
- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. For kicks
    we'll link to the EPT acronym
- prototype:
    int my_function(int val1 [], int val2 [][5]);
- returns:
    TRUE on success, FALSE on failure
- params:
    -- val1 | I | 
            1 = blah blah
                and more blah blah
                plus blah

            2 = blah blah blah

            0 = turn beacon on
    -- val2 | I |
            *1* = blah blah

            *2* = blah blah blah
- example:
    rc = my_function(val);

    if(rc != 0)
    {
        printf("Uh oh, something bad happened!n");
    }

- pseudocode:

    // Blah blah blah
    _call_sub_function()

    if(blah)
    {
        // Do something else
        _call_sub_function2()
    }
    
- see also:
    THis is a test

@h3 @functionsummary

@text
The @functionsummary tag creates a summary table of all prototypes
cross referenced or defined within the document. In this document we've
defined a single prototype my_function which should show up
automatically when this tag is inserted into the document. Additionally
if source code is included any prototypes would automatically get picked
up in this table.

@shorte
\@functionsummary

@text
Generates:

@functionsummary


@h3 @typesummary

@text
The @typesummary tag creates a summary of all structures or enumerations
defined within the document or in any parsed source code.

@shorte
\@typesummary

@text
Generates:

@typesummary


@h2 Source Code Tags

@text
Shorte was built with technical documentation in mind so it supports
including a variety of source code snippets. These are described in the
following section.

@h3 Executing Snippets

@text
In many cases the code within these tags can be executed and the results captured
within the document itself. This is useful for validating example code.
Execution is done bu adding the following attribute:

    exec="1"

to the tag. Remote execution is also possible if SSH keys are setup by
adding the machine="xxx" and port="xxx" parameters.

@h3 @c

@text
The @c tag is used to embed C code directly into the document and
highlight it appropriately. For example, the following block of code
inlines a C snippet. The code can also be run locally using g++ by
passing the exec="1" attribute. See [[->Executing Snippets]] for
more information on setting up Shorte to execute code snippets.

@shorte
\@c: exec="1"
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("hello world!\n");
    return EXIT_SUCCESS;
}

@text
This renders the following output:

@c: exec="1"
#include <stdio.h>
#include <stdlib.h>
int main(void)
{
    printf("hello world!\n");
    return EXIT_SUCCESS;
}

@h3 @python

@text
This tag is used to embed Python code directly into the document and
highlight it appropriately. If the code is a complete snippet it can
also be executed on the local machine and the results returned. See [[->Executing Snippets]]
for more information on setting up Shorte to execute code snippets.

@shorte
\@python: exec="1"
print "Hello world!"

@text
This will execute the code on the local machine and return the output:

@python: exec="1"
print "Hello world!"

@h3 @bash

@text
This tag is used to embed bash code directly into the document and
highlight it appropriately.

@h3 @perl

@text
This tag is used to embed Perl code directly into the document and
highlight it appropriately.

@h3 @shorte

@text
This tag is used to embed Shorte code directly into the document and
highlight it appropriately.

@h3 @d

@text
This tag is used to embed D code directly into the document and
highlight it appropriately.

@h3 @sql

@text
This tag is used to embed SQL code directly into the document and
highlight it appropriately.

@h3 @java

@text
This tag is used to embed Java code directly into the document and
highlight it appropriately.

@h3 @tcl

@text
This tag is used to embed TCL code directly into the document and
highlight it appropriately.

@h3 @vera

@text
This tag is used to embed Vera code directly into the document and
highlight it appropriately.

@h3 @code

@text
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

@text
TBD: add description of this tag.

@h2 Other Tags

@text
The following section describes some of the other more obscure
tags that Shorte supports.

@h3 @inkscape

@text
This allows including SVG files from Inkscape direction in the document. It
requires Inkscape to be installed and the path properly configured. SVG files
are automatically converted to .png files for inclusion since SVG files aren't
widely supported.

@h3 @checklist

@text
The @checklist tag creates a non-interactive checklist

@checklist: caption="test" title="test"
- one: caption="blah blah blah" checked="yes"
- two
- three: checked="yes"
- four

@h3 @acronyms

@text


@acronyms
- Acronym | Definition
- EPT     | Egress Parser Table
- EPC     | Egress Parser CAM

@h3 @embed

@text
TBD - Add description of this tag

@h2 Sequence Diagrams

@text
Shorte allows for automatic generation of sequence diagrams using the @sequence
tag. The syntax is similar to creating a table. This section describes some
examples of creating sequence diagrams.

@h3 @sequence

@text
This tag is used to generate a sequence diagram.

@shorte
\@sequence: title="Sequence Diagram Title" caption="Sequence diagram caption"
- Type    | Source   | Sink         | Name                   | Description

- message | Master   | Slave        | Sync Message           | A sync message sent from master to slave.
- message | Slave    | Master       | Sync Response          | A response message from the slave.
- action  | Slave    |              | Random Event           | A random event on the slave.

@text
The above code generates a sequence diagram that looks something like this:

@sequence: caption="Sequence diagram caption" title="Sequence Diagram Title"
- Type    | Source   | Sink         | Name                   | Description

- message | Master   | Slave        | Sync Message           | A sync message sent from master to slave.
- message | Slave    | Master       | Sync Response          | A response message from the slave.
- action  | Slave    |              | Random Event           | A random event on the slave.

@h1 Test Cases

@text
Shorte allows the creation of test reports that include a summary section
which links to the results of a particular test case defined by the @testcase tag.

@h3 @testcasesummary

@text
The @testcasesummary creates a summary of all the test cases defined in
the document.

Adding this block of code:

@shorte
\@testcasesummary

@text
Will expand to:

@testcasesummary


@h3 @testcase

@text
The @testcase tag is used to define information about a testcase.
It looks something like this:

@shorte
\@testcase
:name: Version
:desc:
This is a diagnostic method that is used to retrieve the
API version information. It reads the version string from the API
and does a very simple check to validate the sanity of the
version string.

:status: PASSED
:duration: 0.100000 sec

\@testcase
:name: Register test
:desc:
This test validates basic register access
by reading the ASIC IDs and verifying the match the
expected value.

:status: PASSED
:duration: 10.480000 sec


\@testcase
:name: Register dump test
:desc:
This test validates the register dump
from the API. Due to restrictions in SWIG it is impossible
to test all the methods so it uses a high-level print
method to display the register dump.

:status: PASSED
:duration: 11.760000 sec

@text
When rendered these examples look like:

@h4 Version

@testcase
:name: Version
:desc:
This is a diagnostic method that is used to retrieve the
API version information. It reads the version string from the API
and does a very simple check to validate the sanity of the
version string.

:status: PASSED
:duration: 0.100000 sec

@h4 Register test

@testcase
:name: Register test
:desc:
This test validates basic register access
by reading the ASIC IDs and verifying the match the
expected value.

:status: PASSED
:duration: 10.480000 sec

@h4 Register dump test

@testcase
:name: Register dump test
:desc:
This test validates the register dump
from the API. Due to restrictions in SWIG it is impossible
to test all the methods so it uses a high-level print
method to display the register dump.

:status: PASSED
:duration: 11.760000 sec

