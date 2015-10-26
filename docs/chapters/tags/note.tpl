@body

@h3 @note
The @note tag is used to create notes within a document. The content
of the note is parsed the same way as an @text section. Here
is an example of a note:

@shorte: exec=True
\@note
This is a note here that I want to display

@h A more complex note
As with @text blocks you can do more complex things like
create lists or inline code blocks:

@shorte: exec=True
\@note
This is a note with some more details:

- It has a list
  - With some data

And another paragraph.

    an indented code block

And even a nested table:

@{table,
- Col 1  | Col 2,
- Data 1 | Data 2
}

