# The document always starts with a heading. The heading
# is anything before the body tag which starts the document
# content.
@doctitle An Example Document
@docsubtitle A subtitle for this example

# A version to associate with the document
@docversion 1.0

@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual

@body

# The @h1 tag is used to create a top level header.
@h1 An Introduction

It is assumed that a heading tag is implictly followed
by an @text tag. This creates a text block which is the
most common tag.

@text
You can also start new text blocks with the @text
tag.

The @table tag creats a table:

@table: title="An Example Table"
-h Heading 1 | Heading 2
-s SubHeading 1 that Spans
-  Column 1  | Column 2

@h2 A Second Level Heading
This heading could have an image:

#@image: src="./my_image.png"
