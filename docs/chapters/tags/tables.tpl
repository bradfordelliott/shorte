@body

@h2 Tables

@h3 @table
The @table tag is used to create a table. The syntax is shown in the
example below.

@shorte: exec=True
\@table
- Header Col 1 | Header Col 2
- Field 1      | Field 2
- Field 3      | Field 4
-s Section
- Field 5      | Field 6

@h4 Spanning Columns
@text
Spanning columns is accomplished by using one or more ||
after the column to span. Each additional | spans an extra column.

@shorte: exec=True
\@table
- Column 1 | column 2 | Column 3 | Column 4 | Column 5
- This column spans the whole table
-s So does this header
- || Blah blah || Blah blah
-s This row has no spanning
- one | two | three | four | five

@h4 Headings and Sub-headings
@text
The first row in the table is generally treated as the header. You can
mark any row as a header row by staring the line with -h. Subheaders
can be created by starting the line with -s.

@shorte: exec=True
\@table
- My Heading 1
-h Also a heading
-s This is a sub-heading

@h4 Table Caption
To create a caption for a table you can use the @{b,caption} attribute:

@shorte: exec=True
\@table: caption="This is a caption for my table"
- My table
- My data | some more data

@h4 Table Title
To add a title to the table you can use the @{b,title} attribute:

@shorte: exec=True
\@table: title="This is my table" caption="This is a random caption"
- My table
- My data | some more data

