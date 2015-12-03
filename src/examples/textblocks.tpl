@doc.title Text Block
@doc.subtitle Examples
@doc.version 1.0
@doc.number 12345

@doc.revisions
- Version | Date           | Author | Description
- 1.0     | 04 March, 2011 | BE     | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | BE     | Something else



@body

@h1 Text Blocks
@text
This is a test of a text block. I've added some quotes like '
and " to ensure they get translated correctly in the PDF file.

Make sure arrays[4] don't get hyperlinked.

Make sure links work [Testlink](http://www.inphi.com/) within the context
of a paragraph [paragraph](http://www.inphi.com/)

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
-h One  | Two  | Three
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
-h h1 | h2
- d1 | d2
}
  - two
    @{quote, This is a quote block inside a bullet point}
- three

An inline table after a list
@{table,
-t Test Title
-h One | Two | Three
- Four | Five | Six
}

A final @{hl,highlighted paragraph} with some @{b,bold data} and some @{star,starred text}.

This is the end of the text block with some @{i, italic text}. This is also a @{starred, starred} block of text.

This line contains some XML chararcters like < and >

@table: title="This is a test"
- One | Two
- A   | Some XML characters < and >

@note
This is a test of a note.

@quote
This is a quote block
with several lines

@c
// This is a line comment
int main(void)
{
    printf("Hello world!\n");

    // This is just a block of test code
    if(x < 10)
    {
        printf("Some other random string\n");
    }

    return 0;
}

@h1 Another section

@text
With a new paragraph and some @{b,bold} text
and a list:

- list
  - list1
  - list2

@h2 A second level heading
With a table
@{table,
- One   | Two
- Three | Four
}

@h3 A third level heading
With some more text here

and a new paragraph

and a block of C code

@c
// This is a C comment
int main(void)
{
}

@h4 A fourth level heading
SOme random text

@h5 A fifth level heading
With some more random text.

@tbd
This stuff still needs to be determined!

@warning
This is a warning. Let's see what it is displayed as

@table: title="My Table" caption="""This is my multiline
 
caption for my table
"""
- One   | Two
- Three | Four
