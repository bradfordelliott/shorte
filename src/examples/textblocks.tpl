@doctitle Text Block
@docsubtitle Examples

@body

@h1 Text Blocks
@text
This is a test of a text block. I've added some quotes like '
and " to ensure they get translated correctly in the PDF file.

Make sure arrays[4] don't get hyperlinked.

This is some inline pre text
@{pre,
This is some pre text
that wraps across multiple
lines
}

What about special characters in a like this: [[http://www.cortina-systems.com, link with <> and ' and "]].

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
    @{code,A nested code block inside a list}
  - another bullet point
    - some more data
    @{table,
- h1 | h2
- d1 | d2
}
  - two
    @{quote, This is a quote block inside a bullet point}
- three

An inline table after a list
@{table,
-t Test Title
- One | Two | Three
- Four | Five | Six
}

A final @{hl,highlighted paragraph} with some @{b,bold data} and some @{star,starred text}.

This is the end of the text block with some @{i, italic text}. This is also a @{starred, starred} block of text.

@table: title="This is a test"
- One | Two
- A   | B

@note
This is a test of a note.

@c
int main(void)
{
    return 0;
}

@h1 Another section

@text
With a new paragraph and some @{b,bold} text
and a list:

- list
  - list1
  - list2

and a table
@{table,
- One   | Two
- Three | Four
}
