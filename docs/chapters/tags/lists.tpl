@body

@h2 Creating Lists
The @ul and @ol tags are typically used to create lists. This mirrors
the HTML constructs <UL> and <OL>.

@h3 @ul
The @ul tag is used to create an unordered list similar to the *ul* tag
in HTML. Lists can currently be indented 5 levels deep.

@shorte: exec=True
\@ul
- Item 1
  - Subitem a
    - Sub-subitem y
- Item 2
  - Subitem b

@text
Using inline styling you can also insert things things like notes or
tables inside each list item:

@shorte: exec=True
\@ul
- Item 1
  @{table,
- H1 | H1
- C1 | C1
}
    - Child 1
      @{quote, This is some random quote about this item}
- Item 2
    - Child 2
      - Child 3
        @{note, A note about child 3}
      - Child 4
        @{warning, A warning about child 4}
      - Child 5
        @{code,
Some code associated with Child 5
that is split across multiple lines
}

@h3 @ol
The @ol tag is used to create an unordered list similar to the *ol* tag
in HTML. Lists can currently be indented 5 levels deep.

@shorte: exec=True
\@ol
- Item 1
  - Subitem a
    - Sub-subitem y
- Item 2
  - Subitem b

