@doc.title Lists
@doc.subtitle Shorte Examplse

@body
@h1 Lists
This is a list item
@ul
- One
  - Two
    - Three
  - Four
- Five

@text
A list with some inline elements

@ul
- One
  @{code,
An inline code block associated with One
}
    - One A
      @{quote, A quote associated with A}
- Two
    - Two A
      @{table,
- H1 | H2
- D1 | D2
}

# This tag defines a variable list similar what docbook provides.
@vl
- One   | Two
- Three | Four
- Four  | This is the value of my variable list element that is formatted
          like a textblock.

