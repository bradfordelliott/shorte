@doctitle Document Headings
@doctitle Document Heading Tests
@doc.status draft

@body

# This is a comment

<!--
@h1 Blah blah blah
This is a multi-line comment
blah blah blah
-->

@h1 Heading 1
Some text here

A multiline comment looks like \<!-- my comment here!!! -->.

<!--
@h2 Heading 2
Some more text here
-->This is some more text

@h3 [[MyHeading,@MyHeading]]

@h4 @MyHeading4

@h3 Heading 3
Blah blah blah MyHeading

@note
This is a test

@tbd
This is a tbd

@question
This is a question

@h1 Another section

@warning
This is something to be careful about!!! It contains some really long
text with a new paragraph

like this and then a list
- one
    - two
    - three

and even a table
@{table,
- One | Two
- Three | Four
}

@h1 A final section

@h2 Heading 2
@h3 Heading 3

@h4 A fourth heading
Some more stuff here

@h5 Heading 5

@h: break_before=True
Heading Other

This is some text here

@h1 @h1
This is a top level heading which links with @h1 with
an ampersand up front. Hyperlinking should work if I type
in @MyHeading4.

@include "examples/subheadings.tpl"

@h1 A final heading
Blah blah blah

@include "examples/subheadings.tpl"

@h1 Another final heading
