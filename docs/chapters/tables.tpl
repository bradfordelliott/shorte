@body

@h3 @table
The @table tag is used to create a table. The syntax is shown in the
example below.

@shorte
\@table
- Header Col 1 | Header Col 2
- Field 1      | Field 2
- Field 3      | Field 4
-& Section
- Field 5      | Field 6

@text
This generates the following output:

@table
- Header Col 1 | Header Col 2
- Field 1      | Field 2
- Field 3      | Field 4
-& Section Header
- Field 5      | Field 6

@h4 Spanning Columns
@text
Spanning columns is accomplished by using one or more ||
after the column to span. Each additional | spans an extra column.

@shorte
\@table
- Column 1 | column 2 | Column 3 | Column 4 | Column 5
- This column spans the whole table
-& So does this header
- || Blah blah || Blah blah
-& This row has no spanning
- one | two | three | four | five

@text
This creates a table that looks like this:

@table
- Column 1 | column 2 | Column 3 | Column 4 | Column 5
- This column spans the whole table
-& So does this header
- || Blah blah || Blah blah
-& This row has no spanning
- one | two | three | four | five

@h4 Headings and Sub-headings
@text
The first row in the table is generally treated as the header. You can
mark any row as a header row by staring the line with -*

@shorte
- My Heading 1
-* Also a heading
-& This is a sub-heading

@text
This creates a table that looks like:

@table
- My Heading 1
-* Also a heading
-& This is a sub-heading

@h4 Table Caption
To create a caption for a table you can do the following:

@shorte
\@table: caption="This is a caption for my table"
- My table
- My data | some more data

@text
This creates the following table:

@table: caption="This is a caption for my table"
- My table
- My data | some more data

@h4 Table Title
To add a title to the table you can use the *title* attribute:

@shorte
\@table: title="This is my table"
- My table
- My data | some more data

@text
This creates the following table:

@table: title="This is my table"
- My table
- My data | some more data



