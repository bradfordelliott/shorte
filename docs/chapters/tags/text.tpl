@body

@h2 Text Entry Tags

@h3 @text
The @text tag creates a text block that is automatically
parsed for things like bullets, indentation, or blocks
of code.

You can insert lists:
@shorte: exec=True
- One
  - Two
    - Three

@text
Creating numbered lists can be done using the following syntax:
@shorte
1. One
    1. Two
        1. Three
2. Blah

@shorte
blah blah blah

- An multi-level list
  - A second level in the list
    - A third level in the list

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

@include "chapters/inline_styling.tpl"


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
