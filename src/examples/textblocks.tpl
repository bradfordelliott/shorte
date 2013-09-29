@doctitle Text Block
@docsubtitle Examples

@body

@h1 Text Blocks

@text
This is a test of a text block.

Text blocks can have tables declared in them with the following
syntax:
@{table,
-t Table Title
- One  | Two  | Three
- Four | Five | Six
- Five | Six
}

A new paragraph in a text block that has an unordered list:

- a list
  - some data
    - some more data
  - two
- three

A final @{hl,highlighted paragraph} with some @{b,bold data}.

This is the end of the text block with some @{i, italic text}.

@table: title="This is a test"
- One | Two
- A   | B
