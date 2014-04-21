@doctitle Code Samples
@docsubtitle Some Shorte Examples
@docnumber 23456
@docfilename blah_blah

@docrevisions
- Version | Date           | Description
- 1.0     | 04 March, 2011 | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | Something else
- 1.4.4   | 06 March, 2011 | This is a really long description of the version
                             change here and what changed in the document. It doesn't
                             match the format of the document but whatever.

@body

@h1: if="1"
Test Results

@input: label="Name" type="text" name="my_field" form="review_form" caption="Enter your name"
@input: label="Comments" type="textarea" name="my_field2" form="review_form" caption="Some other caption"
@input: label="Add" type="submit" name="done" form="review_form" caption="Some random stuff here"

@text
This is a test of my_function2() with some more info about my_function. With some more text here

@embed: src="examples/swish_test.swf" width="480"

@h2: if="2"
A Test of Columns
@columns
@column
@text
*Ottawa*
- Brad E.
- Rob M.
- Shawn
- Tarun

@column
@text
*California*
- Brad W.
- Venu
- Huy

@column
@text
*RTP:*
- Rob S.
@endcolumns


@testcasesummary
Blah blah blah

@testcase: category="one"
-- name: Blah
-- desc:
This test is used to verify the operation of the device in
RXAUI mode with both the ingress and egress paths in retimer mode. Only
the MAC interface is enabled in this test. This test may be run with either
an external loopback or using serial loopbacks.

If an external loopback is present this test performs these steps:
- Initialize the ingress and egress paths in RXAUI retimer mode with only the MAC enabled
- Perform some sanity register accesses.
- Send PBERT traffic out the egress direction, loop it back across the external loopback and
  check it in the ingress direction.
- Turn on the PRBS checker and generator and verify the loopback PRBS traffic.

If no external loopback is present the test performs the same steps except
traffic is looped across the line interface using the line serial loopback

-- status: Passed
-- duration: 10.5s

@h2: if="1"
Other tests

@testcase: category="two" cascade="false"
-- name: Blah2
-- desc:
This test is used to verify the operation of the device in
RXAUI mode with both the ingress and egress paths in retimer mode. Only
the MAC interface is enabled in this test. This test may be run with either
an external loopback or using serial loopbacks.

If an external loopback is present this test performs these steps:
- Initialize the ingress and egress paths in RXAUI retimer mode with only the MAC enabled
- Perform some sanity register accesses.
- Send PBERT traffic out the egress direction, loop it back across the external loopback and
  check it in the ingress direction.
- Turn on the PRBS checker and generator and verify the loopback PRBS traffic.

If no external loopback is present the test performs the same steps except
traffic is looped across the line interface using the line serial loopback

-- status: Failed

@testcase: category="two"
-- name: Blah3
-- desc:
This test is used to verify the operation of the device in
RXAUI mode with both the ingress and egress paths in retimer mode. Only
the MAC interface is enabled in this test. This test may be run with either
an external loopback or using serial loopbacks.

If an external loopback is present this test performs these steps:
- Initialize the ingress and egress paths in RXAUI retimer mode with only the MAC enabled
- Perform some sanity register accesses.
- Send PBERT traffic out the egress direction, loop it back across the external loopback and
  check it in the ingress direction.
- Turn on the PRBS checker and generator and verify the loopback PRBS traffic.

If no external loopback is present the test performs the same steps except
traffic is looped across the line interface using the line serial loopback

-- status: Passed

@testcase: category="two"
-- name: Blah4
-- desc:
This test is used to verify the operation of the device in
RXAUI mode with both the ingress and egress paths in retimer mode. Only
the MAC interface is enabled in this test. This test may be run with either
an external loopback or using serial loopbacks.

If an external loopback is present this test performs these steps:
- Initialize the ingress and egress paths in RXAUI retimer mode with only the MAC enabled
- Perform some sanity register accesses.
- Send PBERT traffic out the egress direction, loop it back across the external loopback and
  check it in the ingress direction.
- Turn on the PRBS checker and generator and verify the loopback PRBS traffic.

If no external loopback is present the test performs the same steps except
traffic is looped across the line interface using the line serial loopback

-- status: Passed


@h1 Code Samples
@text
 @{color:red;background-color:blue,This is some text here}
This is a test LEEDS_VLT_SUPPLY_1V_TX with @{u,some} @{color:00ff00,more stuff} @{i,here}

    an indented block @{br}
    some more @{br} stuff here

{{
This is @{u,some} text
}}

another block of text and some stuff

- a list
    - a sub list
- a list item

some more stuff

and some more stuff

@h2 Function Summary
@functionsummary

@h2 Type Summary
@typesummary

@h2 Perl Example
@perl:
    print "Hello world!\n";
    print "Hello world2!\n";

@p Blah blah [[code.html->C Example]] with a link to the EPC

    Some indent here

blah blah blah

@pre
This is some data here with
a few spaces    in it
and      a newline

@p Blah blah *blah some* more
data and     a     few *spaces*

# In the table below we'll use the || sequence
# to span columns. The 'one' field will
# automatically span columns.
@table: title="Blah blah" mark_reserved="true"
- Header    ||     | Blah | Blah
- one
-* two
-& three
- two       | two
-
- three     ||     | XXX  | tmp
- Reserved  ||     | XXX  | tmp


@inkscape: src="examples/temp.svg"

@h3 A Sequence Diagram
@sequence: title="Sequence Diagram" caption="This is a test description"
- Type    | Source | Sink   | Name            | Description
- message | Master | Slave  | [[PTP Request]] | This is a request message that serves some random
                                                purpose that I do not really care about.
- message | Slave  | Master | response        | Response Message that gets sent in response to the
                                                request.
- action  | Slave  | N/A    | Blah            | Blah blah blah

#@sequence:
#- src="A", dest="B", type="bidir", name="blah blah", link="blah_blah.html", description="This is some text"


@h2 Bash Example

@bash: machine="gateway.neterion.com" port="2202" exec="0"
echo "Hello world!"
echo "PWD=`pwd`"

@h2 Java Example
@java: machine="gateway.neterion.com" port="2202" exec="0"

class tmpexample
{  
    public static void main(String args[])
    {
       System.out.println("Hello World!");
    }
}

@h2 C Example
@c: machine="gateway.neterion.com" port="2202" exec="0"

#include "stdio.h"

int main(void)
{
    printf("Hello world!\n");
}

temp = LEEDS_VLT_SUPPLY_1V_TX;



@h2 Vera Example

@vera: machine="gateway.neterion.com" port="2202" exec="0"

program test
{
    printf("Hello World!\n");
}

@h2 Python Example

@python: machine="gateway.neterion.com" port="2202" exec="0"
print "Hello world!"

@h2 Verilog Example
@verilog: machine="gateway.neterion.com" port="2202" exec="0"

module top(a,b);
input a;
input b;

initial
begin
	$display("Hello World\n");
end

endmodule

@h2 TCL Example

@tcl: machine="gateway.neterion.com" port="2202" exec="0"
puts "Hello world!"

@h2 Checklist Example

@p The following demonstrates an example of a primitive checklist.
   Currently checklists are not data driven but in the future they
   will be linked to @{ul,something underlined} @{b,something bold}
   [[[sort of database]]] or offline store.

@h3 With a title and caption

@checklist: title="test" caption="test"
- one: caption="blah blah blah" checked="yes"
- two
- three: checked="yes"
- four

@h3 With no title or caption
@checklist:
- one: caption="blah blah blah" checked="yes"
- two
- three
- four


#@vector: title="blah" caption="blah blah" diagram="show:yes,align:64,bitorder:increment"
#- Field  | Name       | Description
#- 0-8    | Blah       | Blah blah
#- 10     | *Reserved* | Reserved for future use
#- 12     | My field   | da da da
#-
#- 32-63  | TBD        | Something here
#- 64-127 | field2     | This is a description

#@vector: title="blah2" caption="blah blah" diagram="show:yes,align:64,bitorder:increment"
#- Field  | Name       | Description
#- 8b     | Blah       | Blah blah
#- 16b    | *Reserved* | Reserved for future use
#- 8b     | My field   | da da da
#
#- 32b    | TBD        | Something here
#- 64b    | field2     | This is a description



@struct: name="blah2" description="blah blah" diagram="show:yes,align:128,bitorder:decrement"
-- fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@struct: name="blah3" description="blah blah"
-- fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@h3 my_function
@prototype: language="c"
-- function: my_function()
-- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. For kicks
    we'll link to the EPT acronym
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
        
        0 = turn [[[beacon]]] on
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
    _call_sub_function()

    if(blah)
    {
        // Do something else
        _call_sub_function2()
    }
    
    uint32 instance;
    int naxos_instance_bitmap = *((uint32 *) data);

    for (instance = 0; instance < NAXOS_NUM_MAX_INSTANCES; instance++) {
        int port;

        if (!(naxos_instance_bitmap & (1 << instance)) ||
            naxos_isr_count[instance] == (uint32) NULL)
            continue;

        if (my_function2()) {
            dbg_dump(fd, "[\#%-2d] global_interrupt:                    %d\n", 
                     instance, naxos_global_interrupt[instance]);
        }
    }

-- see also:
    THis is a test


@h3 my_function2
@prototype
-- function: my_function2
-- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. For kicks
    we'll link to the EPT acronym
-- prototype:
    cs_status my_function2(int val1 [], int val2 [][5]);
-- returns:
    TRUE on success, FALSE on failure
-- params:
    -- val1 | I |
        1 = blah blah
            and more blah blah
            plus blah;
        
        2 = blah blah blah;
        
        0 = turn [[[beacon]]] on
    -- val2 | I |
        *1* = blah blah
        
        *2* = blah blah blah

@h1 Acronyms

@acronyms
- Acronym | Definition
- EPT     | Egress Parser Table
- EPC     | Egress Parser CAM

@p This is a test

@h2 Questions and Answers
@questions
Q: This is a question with some more info
A: This is the answer to the question with a lot
   of detail that wraps across multiple lines and
   hopefully it will make the HTML look interesting
   but I'm not sure we'll just have to see what
   happens when it's rendered

Q: This is another question with some more information
A: This is the answer to that question

@h4 e_my_test
@enum: name="e_my_test" description="This is a test enum"
-- values:
- Name | Value | Description
- LEEDS_VLT_SUPPLY_1V_TX | 0x0 |  1V supply TX 
- LEEDS_VLT_SUPPLY_1V_RX | 0x1 |  1V supply RX 
- LEEDS_VLT_SUPPLY_1V_CRE | 0x2 |  1V supply digital core 
- LEEDS_VLT_SUPPLY_1V_DIG_RX | 0x3 |  1V supply digital RX 
- LEEDS_VLT_SUPPLY_1p8V_RX | 0x4 |  1.8V supply RX 
- LEEDS_VLT_SUPPLY_1p8V_TX | 0x5 |  1.8V supply TX 
- LEEDS_VLT_SUPPLY_2p5V | 0xf |  2.5V supply 
- LEEDS_VLT_SUPPLY_TP_P | 0x9 |  Test point P 
- LEEDS_VLT_SUPPLY_TP_N | 0x8 |  Test point N 

@h4 e_my_test2
@enum: name="e_my_test2" description="This is a test enum"
-- values:
- Name | Value | Description
- LEEDS_VLT_SUPPLY_1V_TX | 0x0 |  1V supply TX 
- LEEDS_VLT_SUPPLY_1V_RX | 0x1 |  1V supply RX 
- LEEDS_VLT_SUPPLY_1V_CRE | 0x2 |  1V supply digital core 
- LEEDS_VLT_SUPPLY_1V_DIG_RX | 0x3 |  1V supply digital RX 
- LEEDS_VLT_SUPPLY_1p8V_RX | 0x4 |  1.8V supply RX 
- LEEDS_VLT_SUPPLY_1p8V_TX | 0x5 |  1.8V supply TX 
- LEEDS_VLT_SUPPLY_2p5V | 0xf |  2.5V supply 
- LEEDS_VLT_SUPPLY_TP_P | 0x9 |  Test point P 
- LEEDS_VLT_SUPPLY_TP_N | 0x8 |  Test point N 

#@timeline
#- time | Event     | Description
#- 0    | Blah blah | Blah blah blah blah

@imagemap: id="one"
- x | y | Label     | Description
- 0 | 0 | 1         | Blah blah blah

@image: map="one" src="examples/test.png"
