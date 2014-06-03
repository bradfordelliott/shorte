@doctitle Template Tester
@docsubtitle Test File
@docversion 1.0

@body
@h1 Heading 1
@h2 Heading 2
@h3 Heading 3

@table: title="This is my title"
- Heading 1     | Heading 2
-s Subheading 1 | Subheading 2
- Data 1        | Data 2

@c
This is a block of C code

@text
This is a text block with a list in it
- one
    - two
    - three
-

And this is some more text

@c
int main(void)
{
    printf("Hello world!\n");
}

@struct: name="my_struct" description="This is a description of my struct"
-- fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@enum: name="e_loopback" description='''
The loopback interface point
'''
-- values:
- Enum Name                | Enum Value | Enum Description
- LOOPBK_DIGITAL_NEAR_DATA | 0x1        | Digital Near data loopback. Deprecated, replaced by CS4224_LOOPBK_DUPLEX_NEAR_DATA
- LOOPBK_DUPLEX_NEAR_DATA  | 0x1        | Duplex Near data loopback
- LOOPBK_DIGITAL_FAR_DATA  | 0x2        | Digital Far data loopback. Deprecated, replaced by CS4224_LOOPBK_DUPLEX_FAR_DATA
- LOOPBK_DUPLEX_FAR_DATA   | 0x2        | Duplex Far data loopback


@prototype: language="c"
-- function: my_function()
-- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. 

    - It should support lists
        - And sub-items
    
    And new paragraphs.
    
        Indented text partially works but is not particularly
        robust.
        
        and it could use some work

    - Another list
        - With some more info

    @{table,
    -t An inlined table title
    -h Heading One ! Heading Two
    -  Col 1       ! Col 2
    -s Subheading 1
    -  Col 3       ! Col 4
    }

-- prototype:
    int my_function(int val1 [], int val2 [][5]);
-- returns:
    TRUE on success, FALSE on failure
-- params:
    -- val1 | I |
        1 = blah blah
            and more blah blah
            plus blah;
        
        2 = blah blah blah;
        
        0 = turn @{i,beacon} on
    -- val2 | I |
        *1* = blah blah
        
        *2* = blah blah blah

-- example:
    rc = my_function(val);

    if(rc != 0)
    {
        printf("Uh oh, something bad happened!\n");
    }

-- pseudocode:

    // Blah blah blah
    call_sub_function()

    if(blah)
    {
        // Do something else
        my_function();
    }
    

-- see also:
    THis is a test
