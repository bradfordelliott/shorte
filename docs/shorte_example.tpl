# The document always starts with a heading. The heading
# is anything before the body tag which starts the document
# content.
@doc.title An Example Document
@doc.subtitle A subtitle for this example

# A version to associate with the document
@doc.version 1.0

@doc.revisions:
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

@h2 Tables
The @table tag creats a table:

@table: title="An Example Table"
-h Heading 1 | Heading 2
-s SubHeading 1 that Spans
-  Column 1  | Column 2

@h2 Lists
@text
You can create ordered lists using the @{bold,ol} tag:

@ol
- one
  - two
    - three
- four
  - five
      - six

@text
Or unorded lists using the @{bold,ul} tag:

@ul
- one
  - two
    - three
- four
  - five
    - six

@h2 Images
You can insert images using the @image tag:

@image: src="chapters/images/shorte.png" caption="The Shorte Logo"

