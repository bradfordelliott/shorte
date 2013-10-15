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
    result += "more text"
?>

@text
However, this block does get expanded and it expands to the word:

@{b,<?
result = "Conditional text"
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

