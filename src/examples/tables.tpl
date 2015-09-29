@doctitle Table Tests
@docsubtitle Test Cases

@body
@h1: wikiword=TestHeader
This is a test
BLah blah
with some @{b+u+i+hl,underlined bold italics} blah blah
- a list
- a list

a new @{color:ff0000,paragraph}

    some indented text
    some more indented text
    some more text

        some further indented text
    
    a new indented paragraph

@{pre,
Some pre text here
}

some more text in a new paragraph

#@table: caption='''
#This is a test of the table captions
#'''
@table: title="This is a test" caption='''
This is a test of the table captions
'''
- One | Two | TestHeader
- BLah blah
  with some @{u+b+i,underlined bold italics} blah blah
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
  
  some more text in a @{pre,new paragraph}
- Blah blah blah | BLah blah
                   with some @{u+b+i,underlined bold italics} blah blah
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
@table: widths="10,20,20,50" style="micro" width="100%"
- One | Two | Three | Four
- Blah | Blah | blah blah | blah blah
-& Blah 2 | Blah 2 | Blah 3 | Blah 4
- Blah 2 | Blah 2 | Blah 3 | Blah 4
-* Blah 2 | Blah 2 | Blah 3 | Blah 4
- Blah 2 | Blah 2 | Blah 3 | Blah 4
-r Blah 2 | Blah 2 | Blah 3 | Blah 4
- Blah 2 | Blah 2 | Blah 3 | Blah 4
-= Blah 2 | Blah 2 | Blah 3 | Blah 4

@h3 A table with no header
@table
-x One | Two | Three
- One | Two | Three
- One | Two | Three

@h3 A test table for Transport
@table
- Input Key | Possible Key Values Include | Description
-& Basic Parameters
- \-mode | <cs_mx00_cfg_mode_e>        | Configuration Classification

@table
-h Configuration Rules
- tx_if.dplx_line_driver.traceloss | This is a test
- tx_if.blah.another_rule          | This is another rule


# DEBUG BRAD: Haven't updated the parser to support this format yet
#@h3 A table with no header
#@table
#-- rows:
#-x One | Two | Three
#- One | Two | Three
#- One | Two | Three
