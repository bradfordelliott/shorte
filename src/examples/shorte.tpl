@doctitle Shorte Code Examples
@docsubtitle Examples of Formatting Shorte Code

@body

@h1 Shorte Code Examples

Here is a shorte block that will not
be executed:

@shorte
\@h1 This is a test
This is some text with an @h1 tag in the middle
that probably shouldn't be treated as a keyword since
it doesn't start at the beginning of a line

Make sure we format "strings" within double quotes
but we won't escape strings in 'single quotes' since
they don't match natural language rules.

@text
And this is a shorte block that will get
executed. The results will get inserted into
the document right after the shorte block.

@shorte: exec=True
\@h3 Results
This is the result of executing the shorte
block that was just displayed in the document.

- A list item
  - Another list item


