@doctitle Table Tests
@docsubtitle Test Cases

@body
@h1 This is a test
BLah blah
with some __** // underlined bold italics // **__ blah blah
- a list
- a list

a new paragraph

    some indented text
    some more indented text
    some more text

        some further indented text
    
    a new indented paragraph

{{
Some pre text here
}}

some more text in a new paragraph

#@table: caption='''
#This is a test of the table captions
#'''
@table: title="This is a test" caption='''
This is a test of the table captions
'''
- One | Two | Three
- BLah blah
  with some __** // underlined bold italics // **__ blah blah
  - a list
  - a list
  
  a new paragraph
  
      some indented text
      some more indented text
      some more text
  
          some further indented text
      
      a new indented paragraph
  
  {{
  Some pre text here
  }}
  
  some more text in a new paragraph
- Blah blah blah | BLah blah
                   with some __** // underlined bold italics // **__ blah blah
                   - a list
                   - a list

                   a new paragraph

                       some indented text
                       some more indented text

                           an even further indented line

                   a second paragraph

- Blah blah 2 | Blah blah blah
                and some more blah blah blah

@h2 A Table with no Title
@table
- One | Two | Three | Four
- Blah | Blah | blah blah | blah blah
-& Blah 2 | Blah 2 | Blah 3 | Blah 4
- Blah 2 | Blah 2 | Blah 3 | Blah 4
-* Blah 2 | Blah 2 | Blah 3 | Blah 4
- Blah 2 | Blah 2 | Blah 3 | Blah 4
-r Blah 2 | Blah 2 | Blah 3 | Blah 4
- Blah 2 | Blah 2 | Blah 3 | Blah 4

