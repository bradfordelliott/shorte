
@h3 Inline Styling
Inline styling tags can be used to nest other types within
an @text or @markdown block.

They take the format:

    @{i, Some italic text here}

The following inline styling tags are supported:

@table
- Inline Tag           | Supported Templates | Description
- @br                  | html,odt            | An inline break
- @table               | html,odt            | An inline table tag
- @i,@italic,@italics  | html,odt            | Inline italics
- @b,@bold             | html,odt            | Inline bold
- @hl,@hilite,@hilight | html,odt            | Highlight tag
- @pre                 | html,odt            | Unformatted styling similar to HTML <pre>
- @u,@ul,@underline    | html,odt            | Underlined text
- @color               | html,odt            | Colored text
- @span                | html                | Inline styled text
- @cross,@strike       | html,odt            | Crossed text
- @done,@complete      | html,odt            | Complete an action
- @star,@starred       | html,odt            | Mark a block of text with a star
- @img,@image          | html,odt            | Insert an image inline in a block of text
- @note                | html,odt            | Create an inline note
- @warning             | html,odt            | Create an inline warning
- @tbd                 | html,odt            | Create an inline TBD
- @question            | html,odt            | Create an inline question

@h4 Some Inline Styling Examples
@shorte: exec=True
\@text
This block uses inline styling to create some \@{b,bold text},
some \@{ul,underlined text}, and some \@{hl,highlighted text}.
You can also do things like \@{strike,strike out some text}.

You can even create a nested table.
\@{table,
- One | Two
- Three | Four
}

or you can create warnings:
\@{warning, This is some random warning}

or images:
\@{image, src="chapters/images/shorte.png"}

