@doctitle Hello
@docsubtitle World

@body
@h1 Hello There
This is a very simple document to demonstrate the basics of
shorte. The structure of a document is similar to HTML in that it
starts with a document header followed by a document body. Tags
are created using the @tag syntax.

What happens if I type == in a text block?

It supports lists
- one
    - two
- three

and tables:

@{table,
-t My Table
-h Column One ! Column Two
-s Column One ! Column Two
-  Three      ! Four
-r Three      ! Four
}

inlined images:
@{image, src="examples/record_0.png" width="100px" height="100px"}

and a list with an inline table:
- one
    - @{bold,two} 
    - @{strike,striked} 
    - An inlined table
      @{table,
- My Table
- One   ! Two
- Three ! Four}
    - Another list entry with an image:
        @{image, src="examples/record_0.png"}
- two

This is some random stuff here with a link to [[->Example: Dynamic Reconfiguration, dynamically reconfigure something]]

This is some more data

@ul
- ONe
- Two
- Three

# For some reason this doesn't format correctly. The function body doesn't get indented
# properly
@python
def one():
    '''This is a test string'''

    print """This is another string"""

    print "Hello!!!"


@include "examples/headings.tpl"
@include "examples/images.tpl"

@h1 Test
