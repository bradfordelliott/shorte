@doctitle Conditional Text
@docsubtitle Conditional Text Support

@body

@h1 Conditional Text
@text
This is a test of conditional text. This block is escaped
in the source so it expands to nothing and you should just see
a conditional block below:

@pre
<\?
    result = "Conditional text"
    result += " more text"
?>

@text
However, this block does get expanded and it expands to the word:

@{b,<?
result = "Conditional text"
result += " more text"
?>}


@h2: if="DEBUG"
A Debug Header

This heading will only be included if DEBUG is defined. Otherwise
it will be ignored

@h3 Debug Subheader
This heading will also be ignored since conditionals cascade when
used on headers

@h2: if="1"
An included Header

This heading will be included because it ends up evaluating to
1. This heading is a the same level @h2 so it breaks any conditional
cascade caused by the @{b,if="DEBUG"} on the previous @{b,@h2} header.

@h1: skip_if_pdf
This section would only be included if the output template is PDF

@h3 This is a subsection that should be skipped
With some data underneath it

@h1 This section should not be skipped in PDF docs
blah blah blah

@h2: skip_if_pdf
But this heading should!!!

@h3 This heading is also skipped

@h2 But this heading shouldn't
cause it doesn't have the skip_if_pdf tag

@h3: skip_if_pdf
This one is skipped

@h3 But this one isn't


