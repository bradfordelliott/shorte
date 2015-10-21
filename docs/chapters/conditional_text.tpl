@body

@h2 Conditional Text
The Shorte language supports two types of conditional text
- PHP style inline blocks
- Cascading conditionals using the if="xxx" attribute on tags

@h3 PHP Style Code Blocks
These blocks of code are similar to the inline PHP syntax. You use
the `<\? ... \?\>` syntax to inline a block of Python code. Any output
must get assigned to a variable called @{bold,result} which gets returned in
its expanded form. In this way you can conditionally generate text
or use Python to create documentation.

Variables can be passed to the interpreter using the @{bold,-D} command
line parameter similar to the GCC compiler.

@shorte
\<\?
result = ''
if(1):
    result += 'This is some *bold text* here'
if(0):
    result += 'But this line is not included' 
\?\>

@text
When output you will see something like:

<?
result = ''
if(1):
    result += 'This is some *bold text* here'
if(0):
    result += 'But this line is not included' 
?>

@h3 Conditional Attributes
Conditional text is also supported using the @{bold,if=} attribute on a tag.
The if clause is interpreted as a block of Python code so you can make use
of defines passed from the command line using the @{bold,-D} command line option. Keep
in mind that any defines passed from the command line should be interpreted as strings.

For example:

@shorte
# Include this table
\@table: if="1"
- Col 1 | Col2
- Data1 | Data 2

# But not this table
\@table: if="0"
- Col 3  | col 4
- Data 3 | Data 4

@text
will expand to:

# Include this table
@table: if="1"
- Col 1 | Col2
- Data1 | Data 2

# But not this table
@table: if="0"
- Col 3  | col 4
- Data 3 | Data 4

@text
As with inline code blocks you can specify variables to pass
to the @{bold,if} text to evaluate using the @{bold,-D} command line paramter.

An example is shown below:
@shorte
# Include this heading only if -DDEBUG was defined
\@h1: if="DEBUG=='1'"
Random Debug

@text
The @{bold,Random Debug} header can be turned on as follows:

```
shorte -f example.tpl -DDEBUG=1
```

or turned off like this:

```
shorte -f example.tpl -DDEBUG=0
```

@text
Tags in the document header can also use the conditional attribute. For example, you could change the
title of the document with the -D command line option as follows:

@shorte
\@doctitle: if="DEBUG=='1'"
Debug Document
\@doctitle: if="DEBUG=='0'"
Non Debug Document


@h4 Conditional Cascading
Conditional attributes will cascade based on the weight of the tag.
For example, in the block of code below the conditional attribute on @{bold,Heading A} will
cause @{bold,Heading A.1} and @{bold,Heading A.2} to also be excluded but
it affect @{bold,Heading B}.

@shorte
\@h1: if="0"
Heading A

This heading will get turned off

\@h2 Heading A.1
So will this heading

\@h2 Heading A.2
This heading is turned off to

\@h1 Heading B
This heading will still show up.

@text
The following table defines the weight of tags. Conditional
cascade will continue until a tag is encountered that
has a greater or equal weight.

@table: title="Weight of Tags"
- Tag            | Weight
- @h1            | 7
- @include       | 7
- @h2            | 6
- @h3            | 5
- @h4            | 4
- @h5            | 3
- @h             | 2
- @include_child | 1
- all other tags | 0
