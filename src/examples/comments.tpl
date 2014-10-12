@doctitle Comments
@doctitle Comment tests

@body

@h1 Comments
A single line comment takes this format:

  \# This is a single line comment. You shouldn't see the \\ character

A multi-line comment takes this format:

  \<!--
  This is a multi-line comment. You shouldn't see the \\ character
  blah blah blah -->

The following block of text won't show up
because it is in single line comment:

# This should not show up
# This should not show up either

However this text should show up.

The multi-line comment below should not show up.

   <!-- This is my multil-line comment
     that spans multiple lines -->

   <!-- This comment shouldn't show up either -->

However this text should be visible because it is not
commented out.
